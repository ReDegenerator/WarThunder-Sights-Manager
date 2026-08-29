import os
import re
from PIL import Image, ImageDraw

def parse_and_render_blk(blk_path, output_dir):
    if not os.path.exists(blk_path):
        return False, "File .blk not found"

    with open(blk_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    draw_vert = not re.search(r"drawCentralLineVert\s*:\s*b\s*=\s*no", content, re.IGNORECASE)
    draw_horz = not re.search(r"drawCentralLineHorz\s*:\s*b\s*=\s*no", content, re.IGNORECASE)

    raw_lines = []
    raw_quads = []
    
    min_x, max_x = None, None
    min_y, max_y = None, None

    def update_raw_bounds(x, y):
        nonlocal min_x, max_x, min_y, max_y
        if abs(x) > 1.2 or abs(y) > 0.7: return
        if min_x is None:
            min_x, max_x = x, x
            min_y, max_y = y, y
            return
        if x < min_x: min_x = x
        if x > max_x: max_x = x
        if y < min_y: min_y = y
        if y > max_y: max_y = y

    line_pattern = re.compile(r"\bline\s*\{[^}]*line\s*:\s*p4\s*=\s*([-\d.,]+)", re.IGNORECASE)
    for match in line_pattern.finditer(content):
        nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", match.group(1))]
        if len(nums) >= 4:
            x1, y1, x2, y2 = nums[0], nums[1], nums[2], nums[3]
            is_giant = (abs(x2 - x1) > 2.0) or (abs(y2 - y1) > 2.0)
            is_pure_axis = (abs(y1) < 0.005 and abs(y2) < 0.005) or (abs(x1) < 0.005 and abs(x2) < 0.005)
            is_bg = is_giant or is_pure_axis
            raw_lines.append((x1, y1, x2, y2, is_bg))
            if not is_bg:
                update_raw_bounds(x1, y1)
                update_raw_bounds(x2, y2)

    quad_block_pattern = re.compile(r"\bquad\s*\{([^}]+)\}", re.IGNORECASE)
    for block_match in quad_block_pattern.finditer(content):
        block_body = block_match.group(1)
        quad_pts = []
        for key in ["tl", "tr", "br", "bl"]:
            key_match = re.search(rf"\b{key}\s*:\s*p2\s*=\s*([-\d.,]+)", block_body, re.IGNORECASE)
            if key_match:
                xy = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", key_match.group(1))]
                if len(xy) >= 2: quad_pts.append((xy[0], xy[1]))
                    
        if len(quad_pts) == 4:
            xs = [p[0] for p in quad_pts]
            ys = [p[1] for p in quad_pts]
            is_quad_giant = (max(xs) - min(xs) > 2.0) or (max(ys) - min(ys) > 2.0)
            is_quad_axis = (abs(max(ys)) < 0.008 and abs(min(ys)) < 0.008) or (abs(max(xs)) < 0.008 and abs(min(xs)) < 0.008)
            is_bg = is_quad_giant or is_quad_axis
            raw_quads.append((quad_pts, is_bg))
            if not is_bg:
                for pt in quad_pts: update_raw_bounds(pt[0], pt[1])

    game_min_x, game_max_x = -1.0, 1.0
    game_min_y, game_max_y = -0.5, 0.5
    game_w_ratio = game_max_x - game_min_x
    game_h_ratio = game_max_y - game_min_y

    full_render_w = 2400  
    full_scale = full_render_w / game_w_ratio
    full_render_h = int(game_h_ratio * full_scale)

    img_full = Image.new("RGBA", (full_render_w, full_render_h), (255, 255, 255, 255))
    draw_full = ImageDraw.Draw(img_full)
    
    sight_color = (0, 0, 0, 255)
    axis_color = (0, 0, 0, 255)

    def to_full_px(wx, wy):
        px = int((wx - game_min_x) * full_scale)
        py = int((wy - game_min_y) * full_scale)
        return px, py

    fax, fay = to_full_px(0.0, 0.0)
    if draw_vert: draw_full.line([(fax, 0), (fax, full_render_h)], fill=axis_color, width=2)
    if draw_horz: draw_full.line([(0, fay), (full_render_w, fay)], fill=axis_color, width=2)

    for x1, y1, x2, y2, is_bg in raw_lines:
        px1, py1 = to_full_px(x1, y1)
        px2, py2 = to_full_px(x2, y2)
        draw_full.line([(px1, py1), (px2, py2)], fill=sight_color, width=2)

    for pts, is_bg in raw_quads:
        pixel_pts = [to_full_px(pt[0], pt[1]) for pt in pts]
        draw_full.polygon(pixel_pts, fill=sight_color)

    os.makedirs(output_dir, exist_ok=True)
    img_full.save(os.path.join(output_dir, "full.png"), "PNG")

    #generate preview image

    if min_x is None: min_x, max_x, min_y, max_y = -0.1, 0.1, -0.1, 0.1
    raw_width = max_x - min_x
    raw_height = max_y - min_y
    if raw_width <= 0: raw_width = 0.01
    if raw_height <= 0: raw_height = 0.01

    preview_render_w = 1200
    preview_scale = preview_render_w / raw_width
    preview_render_h = int(raw_height * preview_scale)
    if preview_render_h > 3000: preview_render_h = 3000

    padding = 40
    canvas_w = preview_render_w + padding * 2
    canvas_h = preview_render_h + padding * 2

    img_prev = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))
    draw_prev = ImageDraw.Draw(img_prev)

    def to_prev_px(wx, wy):
        px = padding + int((wx - min_x) * preview_scale)
        py = padding + int((wy - min_y) * preview_scale)
        return px, py

    pax, pay = to_prev_px(0.0, 0.0)
    if draw_vert and (0 <= pax <= canvas_w): draw_prev.line([(pax, 0), (pax, canvas_h)], fill=axis_color, width=2)
    if draw_horz and (0 <= pay <= canvas_h): draw_prev.line([(0, pay), (canvas_w, pay)], fill=axis_color, width=2)

    for x1, y1, x2, y2, is_bg in raw_lines:
        px1, py1 = to_prev_px(x1, y1)
        px2, py2 = to_prev_px(x2, y2)
        if is_bg: draw_prev.line([(px1, py1), (px2, py2)], fill=axis_color, width=2)
        else: draw_prev.line([(px1, py1), (px2, py2)], fill=sight_color, width=5)

    for pts, is_bg in raw_quads:
        pixel_pts = [to_prev_px(pt[0], pt[1]) for pt in pts]
        color = axis_color if is_bg else sight_color
        draw_prev.polygon(pixel_pts, fill=color)

    final_width = 260
    scale_down = final_width / canvas_w
    final_height = int(canvas_h * scale_down)
    final_img_prev = img_prev.resize((final_width, final_height), Image.Resampling.LANCZOS)
    final_img_prev.save(os.path.join(output_dir, "preview.png"), "PNG")

    return True, "Both preview files have been successfully generated."