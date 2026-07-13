from PIL import Image, ImageDraw, ImageFont

# Create a blank image with light slate background (248, 250, 252)
img = Image.new('RGB', (1350, 1420), (248, 250, 252))
draw = ImageDraw.Draw(img)

# Colors
bg_slate = (241, 245, 249)
bg_blue = (239, 246, 255)
bg_pink = (253, 242, 248)
bg_yellow = (254, 249, 195)
bg_indigo = (238, 242, 255)
bg_green = (236, 253, 245)

color_slate_500 = (100, 116, 139)
color_slate_900 = (15, 23, 42)
color_slate_600 = (71, 85, 105)

color_blue_500 = (37, 99, 235)       # Stronger blue
color_blue_900 = (30, 58, 138)

color_pink_500 = (236, 72, 153)
color_purple_800 = (91, 33, 182)

color_yellow_500 = (234, 179, 8)
color_amber_900 = (113, 63, 18)

color_indigo_500 = (67, 56, 202)     # Stronger indigo (distinct from blue)
color_indigo_950 = (30, 27, 75)

color_green_500 = (16, 185, 129)
color_arrow = (71, 85, 105)

# Text labels colors
color_yes = (22, 163, 74)
color_no = (220, 38, 38)

# Fonts
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font_title_main = ImageFont.truetype(font_path, 18)
font_sub = ImageFont.truetype(font_path, 8)
font_title = ImageFont.truetype(font_path, 10)
font_desc = ImageFont.truetype(font_path, 9)
font_label = ImageFont.truetype(font_path, 9)

# Draw Title
draw.text((675 - font_title_main.getbbox("Organization onboarding agent flow")[2]//2, 25), 
          "Organization onboarding agent flow", fill=color_slate_900, font=font_title_main)

# Separator Line
draw.line([(50, 60), (1300, 60)], fill=(203, 213, 225), width=1)

def draw_box(draw, x_center, y_center, width, height, sub_text, title_text, desc_lines, fill, outline):
    # Calculate box bounds
    x0 = x_center - (width // 2)
    x1 = x_center + (width // 2)
    y0 = y_center - (height // 2)
    y1 = y_center + (height // 2)
    
    # Draw rounded rectangle
    draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=fill, outline=outline, width=2)
    
    # Draw Sub-header
    bbox = font_sub.getbbox(sub_text)
    draw.text((x_center - (bbox[2] - bbox[0])//2, y0 + 10), sub_text, fill=outline, font=font_sub)
    
    # Draw Title
    bbox = font_title.getbbox(title_text)
    draw.text((x_center - (bbox[2] - bbox[0])//2, y0 + 25), title_text, fill=outline, font=font_title)
    
    # Draw Description Lines
    y_text = y0 + 42
    for line in desc_lines:
        bbox = font_desc.getbbox(line)
        t_color = color_slate_600
        if outline in [color_blue_500, color_blue_900]:
            t_color = color_blue_900
        elif outline == color_purple_800:
            t_color = color_purple_800
        elif outline == color_amber_900 or outline == color_yellow_500:
            t_color = color_amber_900
        elif outline == color_indigo_500:
            t_color = color_indigo_950
        elif outline == color_green_500:
            t_color = color_slate_900
            
        draw.text((x_center - (bbox[2] - bbox[0])//2, y_text), line, fill=t_color, font=font_desc)
        y_text += 13

def draw_arrow(draw, points, color=color_arrow):
    # Draw the lines
    draw.line(points, fill=color, width=2)
    # Draw arrowhead at the last point
    last_pt = points[-1]
    prev_pt = points[-2]
    
    if last_pt[0] == prev_pt[0]: # Vertical line
        if last_pt[1] > prev_pt[1]: # Pointing down
            arrow_pts = [(last_pt[0]-4, last_pt[1]-8), (last_pt[0]+4, last_pt[1]-8), last_pt]
        else: # Pointing up
            arrow_pts = [(last_pt[0]-4, last_pt[1]+8), (last_pt[0]+4, last_pt[1]+8), last_pt]
    else: # Horizontal line
        if last_pt[0] > prev_pt[0]: # Pointing right
            arrow_pts = [(last_pt[0]-8, last_pt[1]-4), (last_pt[0]-8, last_pt[1]+4), last_pt]
        else: # Pointing left
            arrow_pts = [(last_pt[0]+8, last_pt[1]-4), (last_pt[0]+8, last_pt[1]+4), last_pt]
            
    draw.polygon(arrow_pts, fill=color)

# Column centers
c_auth = 275
c_center = 675
c_guest = 1075
c_existing = 910
c_new = 1210

# -----------------
# Draw Boxes
# -----------------
# 1. Start Box (User interaction - pink)
draw_box(draw, c_center, 100, 240, 94, "● USER INTENT ●", "1. Onboard Organization", 
         ["User expresses intention to", "onboard an organization."], bg_pink, color_pink_500)

# 2. Context Gate (Decision Box - yellow)
draw_box(draw, c_center, 220, 240, 94, "□ DECISION □", "2. Is User Authenticated?", 
         ["Checks if user has an active", "authenticated session."], bg_yellow, color_yellow_500)

# 2a. Personalized Greeting (Agent Action - blue)
draw_box(draw, c_auth, 350, 240, 94, "■ AGENT ACTION ■", "2a. Personalized Greeting", 
         ["Greets user by name & acknowledges", "retrieved user data."], bg_blue, color_blue_500)

# 2b. Generic Greeting (Agent Action - blue)
draw_box(draw, c_guest, 350, 240, 94, "■ AGENT ACTION ■", "2b. Generic Greeting", 
         ["Greets guest user with a generic", "onboarding welcome message."], bg_blue, color_blue_500)

# 3a. Collect Org Details - Auth (User interaction - pink)
draw_box(draw, c_auth, 470, 240, 110, "● USER INPUT ●", "3a. Collect Org Details", 
         ["Prompts for Org details: Name, Description, Org", "Email, Org Phone, and user's Position in", "org (e.g. CEO, CFO, IT Manager)."], bg_pink, color_pink_500)

# 3b. Collect Org Details - Guest (User interaction - pink)
draw_box(draw, c_guest, 470, 240, 110, "● USER INPUT ●", "3b. Collect Org Details", 
         ["Prompts for Org details: Name, Description, Org", "Email, Org Phone, and user's Position in", "org (e.g. CEO, CFO, IT Manager)."], bg_pink, color_pink_500)

# 4a. Store Org in DB - Auth (Database Operation - indigo)
draw_box(draw, c_auth, 590, 240, 94, "■ DATABASE ■", "4a. Store Org in DB", 
         ["Saves organization details with status", "UNVERIFIED in the database."], bg_indigo, color_indigo_500)

# 4b. Store Org in DB - Guest (Database Operation - indigo)
draw_box(draw, c_guest, 590, 240, 94, "■ DATABASE ■", "4b. Store Org in DB", 
         ["Saves organization details with status", "UNVERIFIED in the database."], bg_indigo, color_indigo_500)

# 5. Ask for Mobile Number (Agent Action - blue)
draw_box(draw, c_guest, 710, 240, 94, "■ AGENT ACTION ■", "5. Ask for Mobile Number", 
         ["Prompts user to enter their personal", "contact mobile number."], bg_blue, color_blue_500)

# 6. Is Mobile Registered? (Decision Box - yellow)
draw_box(draw, c_guest, 830, 240, 94, "□ DECISION □", "6. Is Mobile Registered?", 
         ["Checks DB for registered mobile number."], bg_yellow, color_yellow_500)

# 6a. Verify Mobile OTP & Authenticate (Agent Action - blue)
draw_box(draw, c_existing, 950, 240, 94, "■ AGENT ACTION ■", "6a. Verify OTP & Retrieve Contact", 
         ["Sends mobile OTP, user verifies, and system", "retrieves existing contact info (Name/Email)."], bg_blue, color_blue_500)

# 6b. Collect Personal Details & Verify (User interaction - pink)
draw_box(draw, c_new, 950, 240, 94, "● USER INPUT ●", "6b. Collect Details & Verify OTP", 
         ["Collects Name/Email, sends mobile OTP,", "and user verifies mobile via OTP."], bg_pink, color_pink_500)

# 7. Database Consolidation & Linking (Database Operation - indigo)
draw_box(draw, c_center, 1070, 240, 94, "■ DATABASE ■", "7. Database Consolidation", 
         ["Links verified contact info (mobile, email, UUID)", "with saved unverified organization lead record."], bg_indigo, color_indigo_500)

# 8. Alert Sales & Show Card (Agent Action - blue)
draw_box(draw, c_center, 1200, 240, 110, "■ AGENT ACTION ■", "8. Alert Sales & Show Card", 
         ["Triggers Sales Representative notification alert,", "renders organization summary card widget,", "and acknowledges user request."], bg_blue, color_blue_500)

# 9. End (Finish Node - green)
draw_box(draw, c_center, 1330, 240, 94, "● FINISHED ●", "9. Onboarding Request Submitted", 
         ["Organization onboarding request is successfully", "submitted and under review."], bg_green, color_green_500)

# -----------------
# Draw Arrows & Connections
# -----------------
# Node 1 -> Node 2
draw_arrow(draw, [(c_center, 147), (c_center, 173)])

# Node 2 -> Node 2a (Yes branch)
draw_arrow(draw, [(c_center, 267), (c_center, 285), (c_auth, 285), (c_auth, 303)])
draw.text((c_center - 130, 270), "Yes", fill=color_yes, font=font_label)

# Node 2 -> Node 2b (No branch)
draw_arrow(draw, [(c_center, 267), (c_center, 285), (c_guest, 285), (c_guest, 303)])
draw.text((c_center + 100, 270), "No", fill=color_no, font=font_label)

# Node 2a -> Node 3a
draw_arrow(draw, [(c_auth, 397), (c_auth, 415)])

# Node 2b -> Node 3b
draw_arrow(draw, [(c_guest, 397), (c_guest, 415)])

# Node 3a -> Node 4a
draw_arrow(draw, [(c_auth, 525), (c_auth, 543)])

# Node 3b -> Node 4b
draw_arrow(draw, [(c_guest, 525), (c_guest, 543)])

# Node 4b -> Node 5
draw_arrow(draw, [(c_guest, 637), (c_guest, 663)])

# Node 5 -> Node 6
draw_arrow(draw, [(c_guest, 757), (c_guest, 783)])

# Node 6 -> Node 6a (Yes branch)
draw_arrow(draw, [(c_guest, 877), (c_guest, 895), (c_existing, 895), (c_existing, 903)])
draw.text((c_guest - 110, 880), "Yes (Registered)", fill=color_yes, font=font_label)

# Node 6 -> Node 6b (No branch)
draw_arrow(draw, [(c_guest, 877), (c_guest, 895), (c_new, 895), (c_new, 903)])
draw.text((c_guest + 50, 880), "No (New User)", fill=color_no, font=font_label)

# Node 4a (Auth DB save) -> Node 7 (Database Consolidation)
draw_arrow(draw, [(c_auth, 637), (c_auth, 1030), (c_center, 1030), (c_center, 1023)])

# Node 6a -> Node 7
draw_arrow(draw, [(c_existing, 997), (c_existing, 1030), (c_center, 1030), (c_center, 1023)])

# Node 6b -> Node 7
draw_arrow(draw, [(c_new, 997), (c_new, 1030), (c_center, 1030), (c_center, 1023)])

# Node 7 -> Node 8
draw_arrow(draw, [(c_center, 1117), (c_center, 1145)])

# Node 8 -> Node 9
draw_arrow(draw, [(c_center, 1255), (c_center, 1283)])

# Save image
img.save('globally_otp_phone_only_after_org_data.png')
print("Flowchart with parallel tracks generated successfully!")
