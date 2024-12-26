#!/usr/bin/env python3

import cv2
import numpy as np
import argparse
import time

print('')
print('C : Toggle Crosshair')
print('M : Cycle through ColorMaps')
print('N : Cycle element color')
print('H : Toggle HUD')
print('A Z: Change Interpolated scale')
print('F V: Contrast')
print('R T: Record and Stop')
print('P : Take Image')
print('W : Toggle Temperature Conversion')
print('Q : quit')

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()

if args.device:
    dev = args.device
else:
    dev = 2

cap = cv2.VideoCapture('/dev/video' + str(dev), cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
width = 256
height = 192
scale = 3
nw = width * scale
nh = height * scale
alpha = 1.0  # Contrast control (1.0-3.0)
colormap = 0
font = cv2.FONT_HERSHEY_SIMPLEX
dispFullscreen = False
cv2.namedWindow('Thermal', cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', nw, nh)
threshold = 2
hud = False
recording = False
elapsed = "00:00:00"
snaptime = "None"
tempConvert = True
white = (255, 255, 255)
red = (80, 80, 255)
green = (0, 255, 0)
blue = (242, 217, 27)
black = (0, 0, 0)
colors = [white, red, green, blue]
color_index = 0
textColor = white
text_shadow_thickness = 3
display_crosshair = True
crosshair_thickness = 2

def rec():
    now = time.strftime("%Y%m%d--%H%M%S")
    video_out = cv2.VideoWriter(now + 'output.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, (nw, nh))
    return video_out


# tc() : Temperature conversion
def tc(c):
    if tempConvert:
        return "{:.2f} F".format((c * 9 / 5) + 32)
    else:
        return "{:.2f} C".format(c)


def snapshot(heatmap):
    # I would put colons in here, but it Win throws a fit if you try and open them!
    now = time.strftime("%Y%m%d-%H%M%S")
    snap_time = time.strftime("%H:%M:%S")
    cv2.imwrite("TC001" + now + ".png", heatmap)
    return snap_time


def osm(pos):
    print("on-screen menu", pos)


while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        imageData, thermalData = np.array_split(frame, 2)
        hi = thermalData[96][128][0]
        lo = thermalData[96][128][1]
        lo = lo.astype(np.uint16) * 256
        rawTemp = hi + lo
        temp = (rawTemp / 64) - 273.15
        temp = round(temp, 2)
        # TODO: fix this -> find the max temperature in the frame
        lomax = thermalData[..., 1].max()
        posmax = thermalData[..., 1].argmax()
        # since argmax returns a linear index, convert back to row and col
        mcol, mrow = divmod(posmax, width)
        himax = thermalData[mcol][mrow][0]
        lomax = lomax.astype(np.uint16) * 256
        maxtemp = himax + lomax
        maxtemp = (maxtemp / 64) - 273.15
        maxtemp = round(maxtemp, 2)
        # find the lowest temperature in the frame
        lomin = thermalData[..., 1].min()
        posmin = thermalData[..., 1].argmin()
        # since argmax returns a linear index, convert back to row and col
        lcol, lrow = divmod(posmin, width)
        himin = thermalData[lcol][lrow][0]
        lomin = lomin.astype(np.uint16) * 256
        mintemp = himin + lomin
        mintemp = (mintemp / 64) - 273.15
        mintemp = round(mintemp, 2)
        # find the average temperature in the frame
        loavg = thermalData[..., 1].mean()
        hiavg = thermalData[..., 0].mean()
        loavg = loavg * 256
        avgTemp = loavg + hiavg
        avgTemp = (avgTemp / 64) - 273.15
        avgTemp = round(avgTemp, 2)
        bgr = cv2.cvtColor(imageData, cv2.COLOR_YUV2BGR_YUYV)
        bgr = cv2.convertScaleAbs(bgr, alpha=alpha)  # Contrast
        bgr = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_CUBIC)
        match colormap:
            case 0:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)
                cmapText = 'Bone'
            case 1:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_TURBO)
                cmapText = 'Turbo'
            case 2:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_RAINBOW)
                heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
                cmapText = 'RGB'
            case 3:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_JET)
                cmapText = 'Jet'
            case 4:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_DEEPGREEN)
                cmapText = 'Deep Green'
            case 5:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_OCEAN)
                cmapText = 'Ocean'
            case 6:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_HOT)
                cmapText = 'Hot'
            case 7:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_INFERNO)
                cmapText = 'Inferno'
            case 8:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_TWILIGHT_SHIFTED)
                cmapText = 'Twilight Shifted'
            case 9:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_VIRIDIS)
                cmapText = 'Viridis'
            case 10:
                heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_CIVIDIS)
                cmapText = 'Cividis'

        colorMapsLen = 11  # last colormap number + 1
        # UNUSED COLORMAPS
        # [COLORMAP_HSV, COLORMAP_SUMMER, COLORMAP_WINTER, COLORMAP_TWILIGHT, COLORMAP_PARULA, COLORMAP_COOL, COLORMAP_PINK, COLORMAP_MAGMA]

        # draw crosshairs
        if display_crosshair:
            cv2.line(heatmap, (int(nw / 2), int(nh / 2) + 20), (int(nw / 2), int(nh / 2) - 20), textColor, crosshair_thickness)  # vline
            cv2.line(heatmap, (int(nw / 2) + 20, int(nh / 2)), (int(nw / 2) - 20, int(nh / 2)), textColor, crosshair_thickness)  # hline
            cv2.line(heatmap, (int(nw / 2), int(nh / 2) + 20), (int(nw / 2), int(nh / 2) - 20), black, 1)  # vline
            cv2.line(heatmap, (int(nw / 2) + 20, int(nh / 2)), (int(nw / 2) - 20, int(nh / 2)), black, 1)  # hline
            cv2.putText(heatmap, tc(temp), (nw - 77, nh - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, black, text_shadow_thickness, cv2.LINE_AA)
            cv2.putText(heatmap, tc(temp), (nw - 77, nh - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, textColor, 1, cv2.LINE_AA)

        if recording:
            cv2.putText(heatmap, "Rec: " + elapsed, (nw - 100, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, black, 2, cv2.LINE_AA)
            cv2.putText(heatmap, "Rec: " + elapsed, (nw - 100, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)

        if hud:
            cv2.putText(heatmap, 'Avg: ' + tc(avgTemp), (10, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)
            cv2.putText(heatmap, cmapText, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)
            cv2.putText(heatmap, 'Scaling: ' + str(scale) + ' ', (10, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)
            cv2.putText(heatmap, 'Contrast: ' + str(alpha) + ' ', (10, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)
            cv2.putText(heatmap, 'Snapshot: ' + snaptime + ' ', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, textColor, 1, cv2.LINE_AA)
            # display floating max temp
            if maxtemp > avgTemp + threshold:
                # TODO : get actual highest value
                cv2.circle(heatmap, (mrow * scale, mcol * scale), 2, black, 2)
                cv2.circle(heatmap, (mrow * scale, mcol * scale), 2, red, -1)
                cv2.putText(heatmap, tc(maxtemp), ((mrow * scale) + 10, (mcol * scale) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, black, text_shadow_thickness, cv2.LINE_AA)
                cv2.putText(heatmap, tc(maxtemp), ((mrow * scale) + 10, (mcol * scale) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, textColor, 1, cv2.LINE_AA)
            # display floating min temp
            if mintemp < avgTemp - threshold:
                cv2.circle(heatmap, (lrow * scale, lcol * scale), 2, white, 2)
                cv2.circle(heatmap, (lrow * scale, lcol * scale), 2, blue, -1)
                cv2.putText(heatmap, tc(mintemp), ((lrow * scale) + 10, (lcol * scale) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, black, text_shadow_thickness, cv2.LINE_AA)
                cv2.putText(heatmap, tc(mintemp), ((lrow * scale) + 10, (lcol * scale) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, textColor, 1, cv2.LINE_AA)

        # display image
        cv2.imshow('Thermal', heatmap)
        if recording:
            elapsed = (time.time() - start)
            elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            videoOut.write(heatmap)

        keyPress = cv2.waitKey(1)
        match keyPress:
            # print(ord('a')) # print the keycode of desired key
            case 97:
                scale += 1
                if scale >= 5:
                    scale = 5
                nw = width * scale
                nh = height * scale
                if not dispFullscreen:
                    cv2.resizeWindow('Thermal', nw, nh)
            case 122:
                scale -= 1
                if scale <= 1:
                    scale = 1
                nw = width * scale
                nh = height * scale
                if not dispFullscreen:
                    cv2.resizeWindow('Thermal', nw, nh)
            case 99:
                if display_crosshair:
                    display_crosshair = False
                else:
                    display_crosshair = True
            case 102:
                alpha += 0.1
                alpha = round(alpha, 1)
                if alpha >= 3.0:
                    alpha = 3.0
            case 118:
                alpha -= 0.1
                alpha = round(alpha, 1)
                if alpha <= 0:
                    alpha = 0.0
            case 104:
                if hud:
                    hud = False
                elif not hud:
                    hud = True
            case 109:
                colormap += 1
                if colormap == colorMapsLen:
                    colormap = 0
            case 110:
                color_index = color_index + 1
                if color_index == len(colors):
                    color_index = 0
                textColor = colors[color_index]
            case 114:
                if not recording:
                    videoOut = rec()
                    recording = True
                    start = time.time()
            case 116:
                recording = False
                elapsed = "00:00:00"
            case 112:
                snaptime = snapshot(heatmap)
            case 113:
                cv2.destroyAllWindows()
                exit(0)
            case 119:
                if tempConvert:
                    tempConvert = False
                else:
                    tempConvert = True
            case 81:
                print("left arrow key pressed")
            case 84:
                print("down arrow key pressed")
            case 82:
                print("up arrow key pressed")
            case 83:
                print("right arrow key pressed")