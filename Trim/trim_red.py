from PIL import Image

def check(i):
    if i[0] > 5:
        return True
    else:
        return False


im = Image.open("./av_extend_red_left.png")

[xs, ys] = im.size


for i in range(xs):
    for j in range (ys):
        color = im.getpixel((i,j))
        left = (max(0,i - 1),j)
        right = (min(xs - 1,i + 1),j)
        if check(color):
            if check(im.getpixel(left)) != check(im.getpixel(right)):
                im.putpixel((i,j),(0,0,0))

lines = []

for i in range(xs):
    for j in range (ys):
        color = im.getpixel((i,j))
        if check(color):
            lines.append((i,j))


for point in lines:
    im.putpixel(point,(0,0,0))
    im.putpixel((min(xs - 1,point[0]+0),point[1]),(255,0,0))
    im.putpixel((min(xs - 1,point[0]+1),point[1]),(255,0,0))
            

im.show()

im.save("./trim_red.PNG")
