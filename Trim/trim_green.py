from PIL import Image

def check(i):
    if i[1] > 5:
        return True
    else:
        return False


im = Image.open("./av_extend_green_left.png")

[xs, ys] = im.size


for j in range (ys):
    for i in range(xs):
        color = im.getpixel((i,j))
        top = (i,max(0,j - 1))
        bottom = (i,min(ys - 1,j+1))
        if check(color):
            if check(im.getpixel(top)) != check(im.getpixel(bottom)):
                im.putpixel((i,j),(0,0,0))

lines = []

for i in range(xs):
    for j in range (ys):
        color = im.getpixel((i,j))
        if check(color):
            lines.append((i,j))


for point in lines:
    im.putpixel(point,(0,0,0))
    im.putpixel((point[0],min(ys - 1,point[1] + 0)),(0,255,0))
    im.putpixel((point[0],min(ys - 1,point[1] + 1)),(0,255,0))
            

im.show()

im.save("./trim_green.PNG")
