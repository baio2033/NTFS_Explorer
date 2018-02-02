import os, sys
from struct import *

def StringCalcSector2Size(num):
	str_size = ['B', 'KB', 'MB', 'GB']

	t = size = (num * 512)

	for i in range(4):
		t = t / 1024
		if int(t) > 0:
			size = size / 1024
		else:
			break

	return '%.2f %s' % (size, str_size[i])

def LogicalDrivePartition(part, base):
	print 'LogicalDrivePartition'
	start = unpack('<L', part[8:8+4])[0]
	num = unpack('<L', part[12:12+4])[0]

	#print '[L] %10d %s' %(base+start, StringCalcSector2Size(num))

def ExtendedPartition(part, start):
	print 'ExtendedPartition'

	handle.seek((base+start) * 512)
	data = handle.read(0x200)

	if ord(data[510]) == 0x55 and ord(data[511]) == 0xAA:
		print 'PARTITION Read Success'

		part = []

		for i in range(2):
			part.append(data[0x1BE + (i*0x10):0x1BE + (i*0x10) + 0x10])

		if ord(part[0][4]) != 0x0:
			LogicalDrivePartition(part[0], base+_start)
		if ord(part[1][4]) != 0x0:
			start = unpack('<L', part[1][8:8+4])[0]
			ExtendedPartition(part[1], start)

def PrimaryPartition(part):
	global start
	start = unpack('<L', part[8:8+4])[0]
	num = unpack('<L', part[12:12+4])[0]

	print '[P] %10d %s' %(start, StringCalcSector2Size(num))


if __name__ == "__main__":

	hdd = "\\\\.\\PhysicalDrive"
	idx = 0

	while True:
		hdd_name = hdd + str(idx)
		try:
			handle = open(hdd_name, 'rb')

			handle.seek(0*512)

			mbr = handle.read(0x200)

			if ord(mbr[510]) == 0x55 and ord(mbr[511]) == 0xAA:
				#print '\n' + str(idx) + 'th PhysicalDrive'

				part = []

				for i in range(4):
					part.append(mbr[0x1BE + (i*0x10):0x1BE + (i*0x10) + 0x10])


				for i in range(4):
					p = part[i]
					if ord(p[4]) == 0xF or ord(p[4]) == 0x5:
						base = unpack('<L', p[8:8+4])[0]
						ExtendedPartition(p,0)
					elif ord(p[4]) != 0:
						PrimaryPartition(p)
				idx += 1
			else:
				print 'MBR Read Fail'

			handle.close()
		except:
			break