import numpy as np
import pandas as pd
import cv2
import psycopg2


# Setting connection to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="testuser",
    password="password",
    port=5432)


#cursor connection
cur = conn.cursor()

#database schemani yaratish
# cur.execute("CREATE TABLE colors_name(color_id SERIAL PRIMARY KEY  NOT NULL,color VARCHAR NOT NULL,color_name VARCHAR NOT NULL,hex VARCHAR(50) NOT NULL,R VARCHAR(3) NOT NULL,G VARCHAR(3) NOT NULL,B VARCHAR(3) NOT NULL)")


# read image
img = cv2.imread('color_palette.jpg')

# inserting column names into colors.csv file
index = ["color", "color_name", "hex", "R", "G", "B"]

csv = pd.read_csv('colors.csv', names=index, header=None)

# Global variables to use inside functions
clicked = False
r = g = b = xpos = ypos = 0


# color recognizer function
def recognize_color(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G -
                                                int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if (d <= minimum):
            minimum = d
            cname = csv.loc[i, "color_name"]
            hex_name = csv.loc[i, "hex"]
    #color_name, hex, r, g, b ga insert qilish
    cur.execute("INSERT INTO colors_name(color_name, hex, r, g, b) VALUES(%s, %s, %s, %s, %s)",(cname, hex_name, R, G, B))
    conn.commit()
    print(cname, hex_name, R, G, B) 
    return cname


#mouse_click function, rang ustiga mouseni 2 ta bosilishi kk
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


# Opening image
cv2.namedWindow('Color Recognition App')

# Calling mouse click function
cv2.setMouseCallback('Color Recognition App', mouse_click)


while(1):
    cv2.imshow("Color Recognition App", img)
    if (clicked):
        # cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle
        cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)
        # Creating text string to display( Color name and RGB values )
        text = recognize_color(r, g, b) + ' R=' + str(r) + \
            ' G=' + str(g) + ' B=' + str(b)

        # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
        cv2.putText(img, text, (50, 50), 2, 0.8,
                    (255, 255, 255), 2, cv2.LINE_AA)
        # For very light colours we will display text in black colour
        if(r+g+b >= 600):
            cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        clicked = False

    # Break the loop when user hits 'esc' key
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()

# Closing connection to PostgreSQL
cur.close()
conn.close()
