from PIL import Image, ImageDraw, ImageFont

# Open original image
img = Image.open('globally_otp_phone_only_after_org_data.png')
draw = ImageDraw.Draw(img)

# Clear the old description area
bg_color = (241, 245, 249)
draw.rectangle([(423, 1064), (677, 1104)], fill=bg_color)

# Load font
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font_size = 10  # Use size 10 for better legibility and fit
font = ImageFont.truetype(font_path, font_size)

# Text to draw
lines = [
    "Links verified user profile (existing or new) with",
    "saved organization lead record in database."
]

# Text color (71, 85, 105)
text_color = (71, 85, 105)

# Center of Box 6 is 550
box_center_x = 550

# Vertical starting position
y_start = 1071
line_spacing = 14

for i, line in enumerate(lines):
    bbox = font.getbbox(line)
    text_width = bbox[2] - bbox[0]
    x = box_center_x - (text_width // 2)
    y = y_start + (i * line_spacing)
    draw.text((x, y), line, fill=text_color, font=font)

# Save to temporary file
img.save('updated_image_temp.png')
print("Image updated successfully with new coordinates!")
