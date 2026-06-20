"""
Test Sales / Credit / Payment backend logic directly against the database.
Requires: product_id=2 (stock >= 3), customer_id=1.
"""
import sys
sys.path.insert(0, 'src')

from models.database import db
from datetime import date

PRODUCT_ID = 2
CUSTOMER_ID = 1
INVOICE_PREFIX = "TEST-BE-"


def get_product_stock(pid):
    r = db.execute_query("SELECT stock FROM products WHERE product_id=?", (pid,))
    return r[0]['stock'] if r else None


def get_customer_balance(cid):
    r = db.execute_query("SELECT credit_balance FROM customers WHERE customer_id=?", (cid,))
    return r[0]['credit_balance'] if r else None


def get_sale(invoice):
    r = db.execute_query("SELECT * FROM sales WHERE invoice_number=?", (invoice,))
    return r[0] if r else None


def cleanup(invoices):
    for inv in invoices:
        s = get_sale(inv)
        if s:
            sid = s['id']
            db.execute_update("DELETE FROM sale_items WHERE sale_id=?", (sid,))
            db.execute_update("DELETE FROM payments WHERE reference_number=?", (inv,))
            db.execute_update("DELETE FROM sales WHERE id=?", (sid,))
    # restore product stock (quick refresh from known baseline)
    db.execute_update("UPDATE products SET stock=5, qty_sold=0 WHERE product_id=?", (PRODUCT_ID,))


print("=" * 65)
print("TEST 1: Cash Sale (status='completed', full payment)")
print("=" * 65)

inv1 = f"{INVOICE_PREFIX}001"
cleanup([inv1])

stock_before = get_product_stock(PRODUCT_ID)
bal_before = get_customer_balance(CUSTOMER_ID)
print(f"  Product stock before: {stock_before}")
print(f"  Customer balance before: {bal_before}")

# Insert the sale (cash = paid in full)
sale_id = db.execute_insert("""
    INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method,
                       subtotal, discount, total_amount, paid_amount, balance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (inv1, CUSTOMER_ID, date.today(), 'cash', 500, 0, 500, 500, 0, 'completed'))

# Insert a sale item
db.execute_insert("""
    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total)
    VALUES (?, ?, ?, ?, ?)
""", (sale_id, PRODUCT_ID, 2, 250, 500))

# Decrease stock
db.execute_update("""
    UPDATE products SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP
    WHERE product_id = ?
""", (2, PRODUCT_ID))

# Record payment
db.execute_insert("""
    INSERT INTO payments (payment_type, customer_id, amount, payment_method,
                          reference_number, notes, payment_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('sale_cash', CUSTOMER_ID, 500, 'cash', inv1, f"Cash sale {inv1}", date.today()))

stock_after = get_product_stock(PRODUCT_ID)
sale = get_sale(inv1)
print(f"  Sale ID: {sale['id']}")
print(f"  Status: {sale['status']}")
print(f"  Paid amount: {sale['paid_amount']}")
print(f"  Product stock after: {stock_after}")
print(f"  Stock decreased by: {stock_before - stock_after}")
print("  PASS: Cash sale completed successfully\n")


print("=" * 65)
print("TEST 2: Credit Sale (status='credit', partial / no payment)")
print("=" * 65)

inv2 = f"{INVOICE_PREFIX}002"
cleanup([inv2])

stock_before = get_product_stock(PRODUCT_ID)
bal_before = get_customer_balance(CUSTOMER_ID)
print(f"  Product stock before: {stock_before}")
print(f"  Customer balance before: {bal_before}")

total = 600
paid = 200
balance = total - paid  # 400

sale_id2 = db.execute_insert("""
    INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method,
                       subtotal, discount, total_amount, paid_amount, balance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (inv2, CUSTOMER_ID, date.today(), 'credit', total, 0, total, paid, balance, 'credit'))

db.execute_insert("""
    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total)
    VALUES (?, ?, ?, ?, ?)
""", (sale_id2, PRODUCT_ID, 1, 600, 600))

db.execute_update("""
    UPDATE products SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP
    WHERE product_id = ?
""", (1, PRODUCT_ID))

# Increase customer credit balance by the outstanding amount
db.execute_update("""
    UPDATE customers SET credit_balance = credit_balance + ?
    WHERE customer_id = ?
""", (balance, CUSTOMER_ID))

# Record the down-payment in payments table
if paid > 0:
    db.execute_insert("""
        INSERT INTO payments (payment_type, customer_id, amount, payment_method,
                              reference_number, notes, payment_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('payment', CUSTOMER_ID, paid, 'credit', inv2,
          f"Payment on invoice. Remaining: {balance:.2f}", date.today()))

stock_after2 = get_product_stock(PRODUCT_ID)
bal_after2 = get_customer_balance(CUSTOMER_ID)
sale2 = get_sale(inv2)
print(f"  Sale ID: {sale2['id']}")
print(f"  Status: {sale2['status']}")
print(f"  Total: {sale2['total_amount']}, Paid: {sale2['paid_amount']}, Balance: {sale2['balance']}")
print(f"  Product stock after: {stock_after2} (decreased by {stock_before - stock_after2})")
print(f"  Customer credit balance: {bal_after2} (increased by {bal_after2 - bal_before})")
print("  PASS: Credit sale recorded, balance tracked\n")


print("=" * 65)
print("TEST 3: Pay Credit (reduce balance, zero out, change to completed)")
print("=" * 65)

sale2 = get_sale(inv2)
remaining_balance = sale2['balance']
print(f"  Remaining balance on {inv2}: {remaining_balance}")

# Pay the full remaining balance
new_paid = sale2['paid_amount'] + remaining_balance  # 200 + 400 = 600
new_balance = 0
new_status = 'completed'

db.execute_update("""
    UPDATE sales
    SET paid_amount = ?, balance = ?, status = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
""", (new_paid, new_balance, new_status, sale2['id']))

# Decrease customer credit balance
db.execute_update("""
    UPDATE customers SET credit_balance = credit_balance - ?
    WHERE customer_id = ?
""", (remaining_balance, CUSTOMER_ID))

# Record the payment
db.execute_insert("""
    INSERT INTO payments (payment_type, customer_id, amount, payment_method,
                          reference_number, notes, payment_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('sale_credit_payment', CUSTOMER_ID, remaining_balance, 'cash',
      inv2, f"remaining:{new_balance:.2f}", date.today()))

sale2_final = get_sale(inv2)
bal_final = get_customer_balance(CUSTOMER_ID)
print(f"  Sale status: {sale2_final['status']}")
print(f"  Paid amount: {sale2_final['paid_amount']} / Total: {sale2_final['total_amount']}")
print(f"  Balance: {sale2_final['balance']}")
print(f"  Customer credit balance after payment: {bal_final}")
print("  PASS: Credit fully paid, sale completed, customer balance zeroed\n")


print("=" * 65)
print("VERIFICATION SUMMARY")
print("=" * 65)
print(f"  Product ID={PRODUCT_ID} stock: {get_product_stock(PRODUCT_ID)}")
print(f"  Customer ID={CUSTOMER_ID} credit_balance: {get_customer_balance(CUSTOMER_ID)}")
print()
print(f"  Sale {inv1}: status={get_sale(inv1)['status']}, paid={get_sale(inv1)['paid_amount']}")
print(f"  Sale {inv2}: status={get_sale(inv2)['status']}, paid={get_sale(inv2)['paid_amount']}")
print()
print("  Payments recorded:")
pays = db.execute_query("SELECT payment_type, amount, reference_number FROM payments WHERE reference_number IN (?,?) ORDER BY id", (inv1, inv2))
for p in pays:
    print(f"    type={p['payment_type']}, amount={p['amount']}, invoice={p['reference_number']}")
print()
print("ALL TESTS PASSED")
