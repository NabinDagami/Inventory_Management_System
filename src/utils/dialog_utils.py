import customtkinter as ctk


def size_and_center_dialog(dialog, parent, base_w, base_h,
                           min_w=None, min_h=None):

    if min_w is None:
        min_w = base_w
    if min_h is None:
        min_h = base_h

    dialog.update_idletasks()

    scaling = dialog._get_window_scaling()

    # Physical measurements from Tk (DPI-aware pixels at process DPI awareness level)
    pw = parent.winfo_width()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()

    # Convert to CTk logical units because CTk's geometry() scales WxH by window_scaling
    # (x,y are passed through unscaled, so we compute them in logical units)
    pw_l = pw / scaling
    px_l = px / scaling
    py_l = py / scaling
    sw_l = sw / scaling
    sh_l = sh / scaling

    top_gap = 25
    bottom_gap = 40
    side_margin = 10

    dw = min(base_w, sw_l - 2 * side_margin)
    dh = min(base_h, sh_l - top_gap - bottom_gap)

    x = px_l + (pw_l - dw) // 2
    y = py_l + top_gap

    # keep X on screen (logical units)
    x = max(0, min(x, sw_l - dw - 10))

    # keep Y on screen only (logical units)
    y = max(0, min(y, sh_l - dh - bottom_gap))

    # Debug prints
    print(f"[size_and_center_dialog] scaling={scaling}, base=({base_w}x{base_h}), min=({min_w}x{min_h})")
    print(f"[size_and_center_dialog] physical: parent=({pw}x??)+({px},{py}), screen=({sw}x{sh})")
    print(f"[size_and_center_dialog] logical:  parent=({pw_l:.1f}x??)+({px_l:.1f},{py_l:.1f}), screen=({sw_l:.1f}x{sh_l:.1f})")
    print(f"[size_and_center_dialog] geometry({dw:.0f}x{dh:.0f}+{x:.0f}+{y:.0f})")

    dialog.geometry(f"{dw}x{dh}+{x}+{y}")
    dialog.minsize(min_w, min_h)
