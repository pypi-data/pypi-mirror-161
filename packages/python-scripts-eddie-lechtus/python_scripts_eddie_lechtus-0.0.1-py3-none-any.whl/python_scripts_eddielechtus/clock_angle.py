def clock_angle(hours, minutes):
    hours_angle = 0.5 * (hours * 60 + minutes)
    minutes_angle = minutes * 6

    angle = abs(hours_angle - minutes_angle)
    angle = min(360 - angle, angle)
    angle_big = 360 - angle
    return angle, angle_big


while True:
    hours = int(input("Enter hours: 1-12 \n"))
    minutes = int(input("Enter minutes: 0-60 \n"))
    if 1 <= hours <= 13 and 1 <= minutes <= 61:
        break
    else:
        print("Wrong hour/minutes input. Try again")

print("smallest and biggest angle between hours and minutes: ", clock_angle(hours, minutes))



