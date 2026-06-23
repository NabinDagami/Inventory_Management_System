import customtkinter as ctk


def size_and_center_dialog(dialog, parent, base_w, base_h,
                           min_w=None, min_h=None):
    """Size a dialog (clamped to fit screen) and center it on parent.

    Args:
        dialog: The CTkToplevel or Toplevel to configure.
        parent: The parent widget (used to get screen bounds).
        base_w, base_h: Desired size.
        min_w, min_h: Minimum allowed size (default: base_w, base_h).
    """
    if min_w is None:
        min_w = base_w
    if min_h is None:
        min_h = base_h

    dialog.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()

    dw = base_w
    dh = base_h
    if dw > sw - 40:
        dw = sw - 40
    if dh > sh - 60:
        dh = sh - 60
    if dw < min_w:
        dw = min_w
    if dh < min_h:
        dh = min_h

    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    x = px + (pw - dw) // 2
    y = py + (ph - dh) // 2
    x = max(0, min(x, sw - dw - 10))
    y = max(0, min(y, sh - dh - 30))

    dialog.geometry(f"{dw}x{dh}+{x}+{y}")
