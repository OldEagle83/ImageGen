from PIL import Image, ImageFilter, ImageFont, ImageDraw
from matplotlib import rcParams, AFM
import os.path



# #Open existing image
# OriImage = Image.open('img/drone_shots/MnwxMjA3fDB8MXxzZWFyY2h8MjB8fGRyb25lJTIwc2hvdHN8ZW58MHwwfHx8MTY2NjQ4NTY0NQ.jpg')
# # OriImage.show()
# width, height = OriImage.size
# blurImage = OriImage.filter(ImageFilter.GaussianBlur(20))
#
# title_font = ImageFont.truetype('fonts/Montserrat-VariableFont_wght.ttf', 200)
# title_text = "The Beauty of Nature"
# image_editable = ImageDraw.Draw(blurImage)
#
# image_editable.text((int(width/2), int(height/2)), title_text, (237, 230, 211), font=title_font)
# blurImage.show()

def get_text_dim(text):
    afm_filename = os.path.join(rcParams['datapath'], 'fonts', 'afm', 'ptmr8a.afm')
    afm = AFM(open(afm_filename, "rb"))
    return afm.string_width_height(text)

print(get_text_dim('What the heck?'))



#Save blurImage
# blurImage.save('images/simBlurImage.jpg')
