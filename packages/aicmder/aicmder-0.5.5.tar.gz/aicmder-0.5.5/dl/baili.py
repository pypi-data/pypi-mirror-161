import math


def getAngle(x1, y1, x2, y2):
    inRads = math.atan2(y2 - y1, x2 - x1)
    # We need to map to coord system when 0 degree is at 3 O'clock, 270 at 12 O'clock
    # print(inRads)
    if inRads < 0:
        inRads = abs(inRads)
    else:
        inRads = 2 * math.pi - inRads

    return inRads, math.degrees(inRads)

def cal_offset(x1, y1, x2, y2, scale=20):
    rad, degree = getAngle(x1, y1, x2, y2)
    new_degree = min(degree, 360 - degree)
    rad = math.radians(new_degree)
    y_offset = math.sin(rad) * scale
    x_offset = math.cos(rad) * scale
    
    x_offset,  y_offset = abs(round(x_offset)), abs(round(y_offset))
    # if x2 > x1 and y2 > y1:
    #     pass
    if x2 > x1 and y2 < y1:
        y_offset = -y_offset
    
    if x2 < x1 and y2 < y1:
        y_offset = -y_offset
        x_offset = -x_offset
        
    if x2 < x1 and y2 > y1:
        x_offset = -x_offset
        
    # if x2 > x1 and y2 > y1 + 20:
    #     y_offset += 40
    # print(round(x_offset), round(y_offset), new_degree, x1, y1, x2, y2)
    return round(x_offset), round(y_offset)


def shoot(resp_d, base_center_x, base_center_y):
                    
    for i, enermy in enumerate(resp_d["data"]):
        start_x, end_x, end_y, start_y = enermy["start_x"], enermy["end_x"], enermy["end_y"], enermy["start_y"]
        width = end_x - start_x
        # height = end_y - start_y
        origin_shoot_x = start_x + width / 2
        origin_shoot_y = end_y
        shoot_x, shoot_y = origin_shoot_x, origin_shoot_y
        print(base_center_x, origin_shoot_x, base_center_y, origin_shoot_y)
        # right down
        if base_center_x > origin_shoot_x and base_center_y > origin_shoot_y + 40:
            shoot_y -= 60
            if abs(base_center_x - origin_shoot_x) < 90:
                print("add left")
                shoot_x += 20
            if abs(base_center_y - origin_shoot_y) < 100:
                print("add Y")
                shoot_y += 45
            print("right down")
        if base_center_x > origin_shoot_x and base_center_y < origin_shoot_y + 40:
            shoot_y += 60
            shoot_x += 30
            if abs(base_center_y - origin_shoot_y) < 30:
                shoot_y -= 30
                print("Minus y")
            print("right down2")

        if  base_center_x < origin_shoot_x and base_center_y > origin_shoot_y + 40:
            shoot_x += 20
            # if abs(base_center_x - origin_shoot_x) < 90:
            #     print("add left")
            #     shoot_x += 20
            if abs(base_center_y - origin_shoot_y) < 100:
                print("add Y")
                shoot_y += 20
            print("left down")
        if  base_center_x < origin_shoot_x and base_center_y < origin_shoot_y + 40:
            shoot_y += 40
            if abs(base_center_x - origin_shoot_x) < 40:
                shoot_x += 10
                print("Add x 10")
            if abs(base_center_x - origin_shoot_x) > 140:
                shoot_x += 30
                print("Add x 30")

            if abs(base_center_y - origin_shoot_y) < 90 and abs(base_center_y - origin_shoot_y) > 40:
                shoot_y += 25
                print("Add y 25")
            if abs(base_center_x - origin_shoot_x) > 150 and abs(base_center_y - origin_shoot_y) < 40:
                shoot_y += 35
                print("Add y 35")
            print("left down2")
        # if base_center_y  > end_y + 20:
        #     print("1")
        #     shoot_y = end_y - 50
        # else:
        #     print("2")
        #     shoot_y = end_y + 30

        # if base_center_x  < shoot_x:
        #     if abs(base_center_x  - shoot_x) < 155:
        #         print("3")
        #         shoot_x -= 10
        #     else:
        #         print("4")
        #         shoot_x -= 20
        # else:
        #     print("5")
        #     shoot_x += 10
        # x_offset, y_offset = cal_offset(base_center_x, base_center_y, shoot_x, shoot_y, scale=80)
        resp_d["data"][i]["shoot_x"] = shoot_x
        resp_d["data"][i]["shoot_y"] = shoot_y

        # x_offset, y_offset = cal_offset(325, 199, shoot_x, shoot_y, scale=80)
        # resp_d["data"][i]["shoot_x"] = 580 + x_offset
        # resp_d["data"][i]["shoot_y"] = 285 + y_offset