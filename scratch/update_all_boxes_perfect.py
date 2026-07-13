from PIL import Image, ImageDraw, ImageFont

# Open original image
img = Image.open('globally_otp_phone_only_after_org_data.png')
draw = ImageDraw.Draw(img)

# Colors
bg_slate = (241, 245, 249)
bg_blue = (239, 246, 255)
bg_pink = (253, 242, 248)
bg_yellow = (254, 249, 195)

color_slate_500 = (100, 116, 139)
color_slate_900 = (15, 23, 42)
color_slate_600 = (71, 85, 105)

color_blue_500 = (59, 130, 246)
color_blue_900 = (30, 58, 138)

color_pink_500 = (236, 72, 153)
color_purple_800 = (91, 33, 182)

color_yellow_500 = (234, 179, 8)
color_amber_900 = (113, 63, 18)

# Fonts
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font_sub = ImageFont.truetype(font_path, 8)
font_title = ImageFont.truetype(font_path, 10)
font_desc = ImageFont.truetype(font_path, 9)

def draw_centered_text(draw, text, x_center, y, font, color):
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    x = x_center - (text_width // 2)
    draw.text((x, y), text, fill=color, font=font)

# -----------------
# BOX 4 (X: 420 to 680, Y: 468 to 562)
# -----------------
# Clear
draw.rectangle([(423, 471), (677, 559)], fill=bg_slate)
# Draw
draw_centered_text(draw, "■ PROCESS ■", 550, 494, font_sub, color_slate_500)
draw_centered_text(draw, "4. Check Session & Ask for Mobile Number", 550, 509, font_title, color_slate_900)
draw_centered_text(draw, "Checks session token. If missing, prompts user for", 550, 526, font_desc, color_slate_600)
draw_centered_text(draw, "mobile number.", 550, 538, font_desc, color_slate_600)

# -----------------
# DECISION BOX (X: 420 to 680, Y: 600 to 687)
# -----------------
# Clear
draw.rectangle([(423, 603), (677, 684)], fill=bg_yellow)
# Draw
draw_centered_text(draw, "□ DECISION □", 550, 618, font_sub, color_yellow_500)
draw_centered_text(draw, "Is Mobile Number Existing?", 550, 633, font_title, color_amber_900)
draw_centered_text(draw, "Checks DB for registered mobile or active session", 550, 650, font_desc, color_amber_900)
draw_centered_text(draw, "profile.", 550, 663, font_desc, color_amber_900)

# -----------------
# BOX 5a (X: 90 to 350, Y: 753 to 847)
# -----------------
# Clear
draw.rectangle([(93, 756), (347, 844)], fill=bg_blue)
# Draw
draw_centered_text(draw, "■ VERIFY ■", 220, 778, font_sub, color_blue_500)
draw_centered_text(draw, "5a. Verify Mobile OTP Only", 220, 793, font_title, color_blue_900)
draw_centered_text(draw, "Sends & verifies 6-digit OTP code to registered", 220, 811, font_desc, color_blue_900)
draw_centered_text(draw, "mobile number only.", 220, 824, font_desc, color_blue_900)

# -----------------
# BOX 5b (X: 750 to 999, Y: 753 to 847)
# -----------------
# Clear
draw.rectangle([(753, 756), (996, 844)], fill=bg_pink)
# Draw
draw_centered_text(draw, "■ PROCESS ■", 874, 778, font_sub, color_pink_500)
draw_centered_text(draw, "5b. Collect Personal Details", 874, 793, font_title, color_purple_800)
draw_centered_text(draw, "Prompts for Full Name, Title and personal", 874, 811, font_desc, color_purple_800)
draw_centered_text(draw, "email address (mobile entered in Step 4).", 874, 824, font_desc, color_purple_800)

# -----------------
# BOX 5c (X: 750 to 999, Y: 878 to 972)
# -----------------
# Clear
draw.rectangle([(753, 881), (996, 969)], fill=bg_blue)
# Draw
draw_centered_text(draw, "■ VERIFY ■", 874, 903, font_sub, color_blue_500)
draw_centered_text(draw, "5c. Verify Mobile OTP (Email Future)", 874, 918, font_title, color_blue_900)
draw_centered_text(draw, "Sends & verifies OTP code to mobile number.", 874, 936, font_desc, color_blue_900)
draw_centered_text(draw, "(Email verification is a future capability.)", 874, 949, font_desc, color_blue_900)

# -----------------
# BOX 6 (X: 420 to 680, Y: 1013 to 1107)
# -----------------
# Clear
draw.rectangle([(423, 1016), (677, 1104)], fill=bg_slate)
# Draw
draw_centered_text(draw, "■ PROCESS ■", 550, 1036, font_sub, color_slate_500)
draw_centered_text(draw, "6. Contact Association Saved", 550, 1049, font_title, color_slate_900)
draw_centered_text(draw, "Links verified contact info (mobile & email) with", 550, 1066, font_desc, color_slate_600)
draw_centered_text(draw, "saved organization lead record in database.", 550, 1079, font_desc, color_slate_600)

# Save
img.save('updated_image_temp.png')
print("All flowchart boxes updated successfully including decision box!")
