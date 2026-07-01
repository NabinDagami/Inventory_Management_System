"""
Test sales return backend logic (stock restore + financial adjustments).
"""
import sys
sys.path.insert(0, 'src')

from models.database import db
from datetime import date

PRODUCT_ID = None
CUSTOMER_ID = None
INVOICE_PREFIX = "TEST-RET-"


def setup():
    global PRODUCT_ID, CUSTOMER_ID
    # Ensure a test product exists
    p = db.execute_query("SELECT product_id, stock FROM products WHERE is_active=1 LIMIT 1")
    if p:
        PRODUCT_ID = p[0]['product_id']
    else:
        PRODUCT_ID = db.execute_insert(
            "INSERT INTO products (name, sku, stock, price_normal, price_workshop, cost_price, reorder_level, is_active) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            ("Test Return Product", "TEST-RET-PROD", 10, 100, 80, 50, 5)
        )
        print(f"  Created test product id={PRODUCT_ID}")

    c = db.execute_query("SELECT customer_id, credit_balance FROM customers WHERE is_active=1 LIMIT 1")
    if c:
        CUSTOMER_ID = c[0]['customer_id']
    else:
        CUSTOMER_ID = db.execute_insert(
            "INSERT INTO customers (name, type, is_active) VALUES (?, ?, 1)",
            ("Test Return Customer", "Normal")
        )
        print(f"  Created test customer id={CUSTOMER_ID}")

    # Reset product stock
    db.execute_update("UPDATE products SET stock=10, qty_sold=0 WHERE product_id=?", (PRODUCT_ID,))
    # Reset customer credit
    db.execute_update("UPDATE customers SET credit_balance=0 WHERE customer_id=?", (CUSTOMER_ID,))


def get_stock():
    r = db.execute_query("SELECT stock FROM products WHERE product_id=?", (PRODUCT_ID,))
    return r[0]['stock'] if r else None


def get_credit_balance():
    r = db.execute_query("SELECT credit_balance FROM customers WHERE customer_id=?", (CUSTOMER_ID,))
    return r[0]['credit_balance'] if r else None


def get_sale(invoice):
    r = db.execute_query("SELECT *, id as sale_id FROM sales WHERE invoice_number=?", (invoice,))
    return r[0] if r else None


def get_payments(invoice):
    return db.execute_query("SELECT * FROM payments WHERE reference_number=?", (invoice,))


def create_sale(invoice, total_amount, paid_amount, customer_id=None):
    balance = total_amount - paid_amount
    status = 'completed' if balance <= 0.01 else 'credit'
    sale_id = db.execute_insert("""
        INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method, subtotal, discount,
                          total_amount, paid_amount, balance, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (invoice, customer_id, date.today(), 'cash' if paid_amount == total_amount else 'credit',
          total_amount, 0, total_amount, paid_amount, balance, status))

    # Insert a sale item
    db.execute_insert("""
        INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total)
        VALUES (?, ?, ?, ?, ?)
    """, (sale_id, PRODUCT_ID, 1, total_amount, total_amount))

    # Reduce stock
    db.execute_update("UPDATE products SET stock = stock - 1 WHERE product_id=?", (PRODUCT_ID,))

    # If credit, increase customer credit balance
    if customer_id and balance > 0:
        db.execute_update("UPDATE customers SET credit_balance = COALESCE(credit_balance, 0) + ? WHERE customer_id=?",
                         (balance, customer_id))

    # Record payment
    if paid_amount > 0:
        ptype = 'sale_cash' if paid_amount == total_amount else 'sale_credit_paid'
        db.execute_insert("""
            INSERT INTO payments (payment_type, customer_id, amount, payment_method, reference_number, notes, payment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ptype, customer_id, paid_amount, 'cash', invoice, f"Initial payment", date.today()))

    return sale_id


def process_return(sale_data, refund_amount):
    """Simulate SaleReturnDialog._confirm_return logic"""
    db.execute_update("UPDATE products SET stock = stock + 1, updated_at = CURRENT_TIMESTAMP WHERE product_id=?", (PRODUCT_ID,))

    old_paid = sale_data['paid_amount']
    old_total = sale_data['total_amount']
    new_paid = max(0, old_paid - refund_amount)
    new_total = old_total - refund_amount
    new_balance = max(0, new_total - new_paid)
    new_status = 'completed' if new_balance <= 0.01 else 'credit'

    existing_notes = sale_data.get('notes') or ""
    return_note = f"[Return] {date.today()}: items={{'{PRODUCT_ID}': 1}} refund={refund_amount:.2f}"
    new_notes = (existing_notes + "\n" + return_note) if existing_notes else return_note

    db.execute_update("""
        UPDATE sales SET notes=?, total_amount=?, paid_amount=?, balance=?, status=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (new_notes, new_total, new_paid, new_balance, new_status, sale_data['sale_id']))

    customer_id = sale_data.get('customer_id')
    db.execute_insert("""
        INSERT INTO payments (payment_type, customer_id, amount, payment_method, reference_number, notes, payment_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('sale_return', customer_id, refund_amount, 'cash', sale_data['invoice_number'],
          f"Return on {sale_data['invoice_number']} — 1 item(s) refunded", date.today()))

    if customer_id:
        old_balance = sale_data.get('balance', old_total - old_paid)
        balance_delta = new_balance - old_balance
        if balance_delta != 0:
            db.execute_update("UPDATE customers SET credit_balance = COALESCE(credit_balance, 0) + ? WHERE customer_id=?",
                             (balance_delta, customer_id))


def cleanup(invoices):
    for inv in invoices:
        s = get_sale(inv)
        if s:
            sid = s['id']
            db.execute_update("DELETE FROM sale_items WHERE sale_id=?", (sid,))
            db.execute_update("DELETE FROM payments WHERE reference_number=?", (inv,))
            db.execute_update("DELETE FROM sales WHERE id=?", (sid,))
    db.execute_update("UPDATE products SET stock=10, qty_sold=0 WHERE product_id=?", (PRODUCT_ID,))
    db.execute_update("UPDATE customers SET credit_balance=0 WHERE customer_id=?", (CUSTOMER_ID,))


# ===== TESTS =====
passed = 0
failed = 0

def check(label, condition):
    global passed, failed
    if condition:
        print(f"  [OK] {label}")
        passed += 1
    else:
        print(f"  [FAIL] {label}")
        failed += 1


print("=" * 65)
print("SETUP")
print("=" * 65)
setup()

# =============================================
print("\n" + "=" * 65)
print("TEST 1: Cash sale fully paid -> return $30")
print("=" * 65)
inv1 = f"{INVOICE_PREFIX}001"
cleanup([inv1])

stock_before = get_stock()
credit_before = get_credit_balance()
create_sale(inv1, total_amount=100, paid_amount=100, customer_id=CUSTOMER_ID)
sale = get_sale(inv1)

process_return(sale, refund_amount=30)

sale_after = get_sale(inv1)
check("Stock restored (10->9->10)", get_stock() == stock_before)
check("Total reduced 100->70", sale_after['total_amount'] == 70)
check("Paid reduced 100->70", sale_after['paid_amount'] == 70)
check("Balance stays 0", sale_after['balance'] == 0)
check("Status is completed", sale_after['status'] == 'completed')
check("Credit balance unchanged (was 0)", get_credit_balance() == credit_before)
pays = get_payments(inv1)
return_pay = [p for p in pays if p['payment_type'] == 'sale_return']
check("Return payment record created", len(return_pay) == 1)
check("Return amount = 30", return_pay[0]['amount'] == 30)

# =============================================
print("\n" + "=" * 65)
print("TEST 2: Credit sale (nothing paid) -> return $30")
print("=" * 65)
inv2 = f"{INVOICE_PREFIX}002"
cleanup([inv2])

credit_before = get_credit_balance()
create_sale(inv2, total_amount=100, paid_amount=0, customer_id=CUSTOMER_ID)
sale = get_sale(inv2)
credit_after_sale = get_credit_balance()

process_return(sale, refund_amount=30)

sale_after = get_sale(inv2)
check("Stock restored", get_stock() == 10)
check("Total reduced 100->70", sale_after['total_amount'] == 70)
check("Paid stays 0 (nothing paid)", sale_after['paid_amount'] == 0)
check("Balance reduced 100->70", sale_after['balance'] == 70)
check("Status is credit", sale_after['status'] == 'credit')
check("Credit balance reduced by 30 (100->70)", get_credit_balance() == credit_after_sale - 30)
pays = get_payments(inv2)
return_pay = [p for p in pays if p['payment_type'] == 'sale_return']
check("Return payment record created", len(return_pay) == 1)
check("Return amount = 30", return_pay[0]['amount'] == 30)

# =============================================
print("\n" + "=" * 65)
print("TEST 3: Partial payment credit sale -> return $30")
print("=" * 65)
inv3 = f"{INVOICE_PREFIX}003"
cleanup([inv3])

create_sale(inv3, total_amount=100, paid_amount=40, customer_id=CUSTOMER_ID)
sale = get_sale(inv3)
old_balance = sale['balance']
credit_after_sale = get_credit_balance()

process_return(sale, refund_amount=30)

sale_after = get_sale(inv3)
check("Stock restored", get_stock() == 10)
check("Total reduced 100->70", sale_after['total_amount'] == 70)
check("Paid reduced 40->10", sale_after['paid_amount'] == 10)
check("Balance unchanged (60->60)", sale_after['balance'] == old_balance)
check("Status is credit", sale_after['status'] == 'credit')
check("Credit balance unchanged", get_credit_balance() == credit_after_sale)
pays = get_payments(inv3)
return_pay = [p for p in pays if p['payment_type'] == 'sale_return']
check("Return payment record created", len(return_pay) == 1)
check("Return amount = 30", return_pay[0]['amount'] == 30)

# =============================================
print("\n" + "=" * 65)
print("TEST 4: Refund exceeds paid amount -> paid_amount capped at 0")
print("=" * 65)
inv4 = f"{INVOICE_PREFIX}004"
cleanup([inv4])

create_sale(inv4, total_amount=100, paid_amount=20, customer_id=CUSTOMER_ID)
sale = get_sale(inv4)
credit_after_sale = get_credit_balance()

process_return(sale, refund_amount=50)

sale_after = get_sale(inv4)
check("Stock restored", get_stock() == 10)
check("Total reduced 100->50", sale_after['total_amount'] == 50)
check("Paid capped at 0 (was 20, refund 50)", sale_after['paid_amount'] == 0)
check("Balance 50", sale_after['balance'] == 50)
check("Credit balance reduced (old={}, new={}, delta=-30)".format(credit_after_sale, get_credit_balance()),
      get_credit_balance() == credit_after_sale - 30)
pays = get_payments(inv4)
return_pay = [p for p in pays if p['payment_type'] == 'sale_return']
check("Return payment record created", len(return_pay) == 1)
check("Return amount = 50", return_pay[0]['amount'] == 50)

# =============================================
print("\n" + "=" * 65)
print("RESULTS")
print("=" * 65)
print(f"  Passed: {passed}  Failed: {failed}  Total: {passed + failed}")
if failed:
    print("  !! SOME TESTS FAILED")
else:
    print("  ** ALL TESTS PASSED")

# Cleanup
cleanup([inv1, inv2, inv3, inv4])
print()
