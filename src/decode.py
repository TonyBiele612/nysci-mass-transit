import numpy as np
import math
import cv2 as cv
import matplotlib.pyplot as pt

WINDOW_TITLE = 'window'

img = cv.imread('img.jpg')
height, width = img.shape[0], img.shape[1]
print(height, width)


dictionary = {
  0:   0b1100111010111000101100011010001001110001001,
  1:   0b1000101011111000110001111000000110001011001,
  2:   0b1111101111111111011001010101001010010010101,
  3:   0b0011100001000111101100101100010000100111101,
  4:   0b1001100001100110000111001111011011100011110,
  5:   0b1101100110000000110010011011100101111010111,
  6:   0b0101111100100101000011101010010000101001000,
  7:   0b0100000101110100010010010010100110110001011,
  8:   0b0001101110000100000100010010001010011011000,
  9:   0b1001101011000101110011010001011110110010001,
  10:  0b0010111000010110000100111010100000110110101,
  11:  0b1101111010110101100110100011111010111110000,
  12:  0b0111011011100000110101110010101111111101010,
  13:  0b0010010000000111001110110001001000011101100,
  14:  0b1101010100001101000101000111011011001111111,
  15:  0b1101101111101110001110111101111111011000100,
}


def clamp(x, lo, hi):
  if (x < lo):
    return lo
  elif (x > hi):
    return hi
  else:
    return x

def median(l):
  l = sorted(l)
  middle = round(len(l) / 2)
  if len(l) % 2 == 1:
    return l[middle]
  else:
    return 0.5 * (l[middle - 1] + l[middle])

def bitRotate(x):
  msb = x & (1 << 42)
  mask = (1 << 43) - 1
  shift = (x << 1) & mask
  return shift | (0 if msb == 0 else 1)

def bitCount(x):
  count = 0
  for i in range(43):
    if ((x >> i) & 1 == 0):
      count += 1
  return count

def minimumDistance(x, y):
  distance = bitCount(x ^ y)
  for i in range(42):
    x = bitRotate(x)
    distance = min(distance, bitCount(x ^ y))
  return distance

def matchCode(x):
  for code in dictionary:
    if (minimumDistance(x, dictionary[code]) < 8):
      return code
  return -1



x = 1500
def setX(v):
  global x
  x = v
y = 500
def setY(v):
  global y
  y = v
r = 500
def setR(v):
  global r
  r = v

def decode(roi, r, n=0):
  tau = 2 * 3.141592
  hsv = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
  sampleAngles = [ x * tau / 43 for x in range(43) ]
  samplePositions = list(map(lambda a : (round(r * math.cos(tau - a)) + 256, round(r * math.sin(tau - a)) + 256), sampleAngles))
  sampleValues = list(map(lambda p : hsv[p[1], p[0], 2], samplePositions))
  minVal = min(sampleValues)
  maxVal = max(sampleValues)
  m = (maxVal - minVal) / 2
  m += minVal
  binary = [ 1 if v > m else 0 for v in sampleValues ]
  binStr = ''.join(str(b) for b in binary)
  code = matchCode(int(binStr, 2))
  if (code == -1 and n < 16):
    # try again at a slightly smaller radius
    decode(roi, 0.99*r, n+1)
  else:
    print(code, binStr, n)
    pt.plot(np.array(sampleAngles), np.array(sampleValues))
    pt.plot(np.array(sampleAngles), np.array([m] * len(sampleValues)))
    pt.plot(np.array(sampleAngles), np.array([ 255 * b for b in binary ]))
    pt.show()


def render():
  global x, y, r
  x = clamp(x, 256, width - 256)
  y = clamp(y, 256, height - 256)
  r = clamp(r, 20, 255)
  roi = img[y-256:y+256, x-256:x+256]
  draw = roi.copy()
  cv.circle(draw, (256, 256), r, (0, 255, 0), 2)
  cv.imshow(WINDOW_TITLE, draw)
  k = cv.waitKey(1)
  if (k >= 0):
    k = chr(k)
  if k == 'w':
    y -= 1
  elif k == 'W':
    y -= 10
  elif k == 'a':
    x -= 1
  elif k == 'A':
    x -= 10
  elif k == 's':
    y += 1
  elif k == 'S':
    y += 10
  elif k == 'd':
    x += 1
  elif k == 'D':
    x += 10
  elif k == ',':
    r -= 1
  elif k == '<':
    r -= 10
  elif k == '.':
    r += 1
  elif k == '>':
    r += 10
  elif k == ' ':
    decode(roi, r)
    

while 1:
  render()
