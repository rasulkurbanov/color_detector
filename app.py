import numpy as np
import pandas as pd
import cv2
import psycopg2


#PostgreSQL sozlamalari
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="testuser",
    password="password",
    port=5432)


#cursor bo'glanish
cur = conn.cursor()

#database schemani yaratish
# cur.execute("CREATE TABLE colors_name(color_id SERIAL PRIMARY KEY  NOT NULL,color VARCHAR NOT NULL,color_name VARCHAR NOT NULL,hex VARCHAR(50) NOT NULL,R VARCHAR(3) NOT NULL,G VARCHAR(3) NOT NULL,B VARCHAR(3) NOT NULL)")


#shu papkani ichida turgan rasmni o'qish
img = cv2.imread('color_palette.jpg')

# colors.csv faylimizga ustun nomlarini berib chiqish
index = ["color", "color_name", "hex", "R", "G", "B"]

#pandas yordamida csv fileni o'qish
csv = pd.read_csv('colors.csv', names=index, header=None)

# funksiyani ichida ishlatish uchun global variablelar
clicked = False
r = g = b = xpos = ypos = 0

"""
1.rangni aniqlovchi funksiya, k-NN algoritmi bo'yicha ishlaydi  
2.rangni aniqlash uchun, biz distance(d) qaysi rang eng yaqin holatda ekanligini 
hisoblab minimum holatini olamiz
eng yaqin masofa esa ushbu formula yordamida hisoblanadi
  d = abs(Red — ithRedColor) + (Green — ithGreenColor) + (Blue — ithBlueColor)

"""
def recognize_color(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        #pandas yordamida csv filedagi rowlardan ma'lumotlarni olish
        d = abs(R - int(csv.loc[i, "R"])) + abs(G -
                                                int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if (d <= minimum):
            minimum = d
            cname = csv.loc[i, "color_name"]
            hex_name = csv.loc[i, "hex"]
    #database ichidagi color_name, hex, r, g, b  columnlariga ga data insert qilish
    cur.execute("INSERT INTO colors_name(color_name, hex, r, g, b) VALUES(%s, %s, %s, %s, %s)",(cname, hex_name, R, G, B))
    conn.commit()
    print(cname, hex_name, R, G, B) 
    return cname


"""
mouse_click funksiyasi, event nomi bor, mouse ning x va y positsiyasi bor, qachonki mouse 
2ta bosilgan xpos bilan ypos x,y qiymatlarni oladi
"""
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)


#dasturning desktopdagi nomi
cv2.namedWindow('Color Recognition App')

#dasturimiz ichida rangni ustiga ikkita bosilganda mouse_click funksiyasini ishlatish
cv2.setMouseCallback('Color Recognition App', mouse_click)

#bu loop esa dasturni desktop holatida ishlashini ta'minlaydi
while(1):
    cv2.imshow("Color Recognition App", img)
    if (clicked):
        # cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle
        cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)
        # color_name va RGB qiymatni dasturda ko'rsatish uchun
        text = recognize_color(r, g, b) + ' R=' + str(r) + \
            ' G=' + str(g) + ' B=' + str(b)

        # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
        cv2.putText(img, text, (50, 50), 2, 0.8,
                    (255, 255, 255), 2, cv2.LINE_AA)
        # Judayam och ranglar uchun fonni to'q qilish
        if(r+g+b >= 600):
            cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        clicked = False

    # 'esc' bosilganda loop ni to'xtatish va dasturdan chiqib ketish
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()

# Closing connection to PostgreSQL
cur.close()
conn.close()
