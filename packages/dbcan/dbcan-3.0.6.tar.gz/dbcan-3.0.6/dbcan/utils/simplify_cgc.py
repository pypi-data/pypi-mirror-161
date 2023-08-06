import os
import sys


# def read_file(input_file):
# 	dir = os.path.dirname(input_file)
# 	update_cgc = os.path.join(dir, 'update_cgc.out')
# 	if os.path.exists(update_cgc):
# 		os.remove(update_cgc)
# 	try:
# 		f = open(dir+input_file, 'r')
# 	except:
# 		print('fail to open')
# 		exit(-1)
# 	try:
# 		text = f.read()
# 	except:
# 		print('fail to read')
# 		exit(-1)
# 	finally:
# 		f.close()
# 		text = text.split('\n')
# 	return text,dir

def simplify_output(inFile):
	try:
		text = open(inFile).readlines()
		text = [line.strip() for line in text]
	except:
		print("fail to read")
		exit(-1)
	dir = os.path.dirname(inFile)
	# os.remove(dir+'cgc.out')
	annotation = ''
	if '' in text:
		text.remove('')
	with open(dir + '/cgc_standard.out', 'a') as f:
		f.write("CGC#\tGene Type\tContig ID\tProtein ID\tGene Start\tGene Stop\tDirection\tProtein Family\n")
		f.close()
	for i in range(len(text)):
		simplified_line = []
		if '+++++' not in text[i]:
			each_line = text[i].split('\t')
			simplified_line.append(each_line[4])
			simplified_line.append(each_line[1])
			simplified_line.append(each_line[5])
			simplified_line.append(each_line[8])
			simplified_line.append(each_line[6])
			simplified_line.append(each_line[7])
			simplified_line.append(each_line[9])

			if '' in each_line:
				each_line.remove('')
			if 'TC' in each_line[1]: # need fix split order if needed
				annotation = each_line[10].split('|')[3].split(';')[0]
				simplified_line.append(annotation)
			elif 'CAZyme' in each_line[1]: # need fix split order if needed
				annotation = each_line[10].split(';')[0].split('=')[1]
				simplified_line.append(annotation)
			elif 'STP' in each_line[1]: # need fix split order if needed
				pre_annotation = each_line[10].split(';')[0].split('=')[1].split('|')
				STP_counter = 0
				for i in pre_annotation: #hard code
					if 'STP' in i:
						STP_counter = STP_counter + 1
				if STP_counter > 1:
					pre_annotation = each_line[10].split(';')[0].split('=')[1].split(',')
					STP_list = []
					for STP in pre_annotation:
						if 'STP' in STP:
							STP_list.append(STP.split('|')[1])
					annotation = ('+').join(STP_list)
				elif STP_counter == 1:
					annotation = each_line[10].split(';')[0].split('=')[1].split('|')[1]
				else:
					annotation = 'none'
				simplified_line.append(annotation)
			elif 'TF' in each_line[1]:
				pre_annotation = each_line[10].split(';')[0].split('=')[1].split('|')
				TF_counter = 0
				for i in pre_annotation: #hard code
					if 'DBD-Pfam' in i:
						TF_counter = TF_counter + 1
				if TF_counter > 1:
					pre_annotation = each_line[10].split(';')[0].split('=')[1].split(',')
					TF_list = []
					for TF in pre_annotation:
						if 'DBD-Pfam' in TF:
							TF_list.append(TF.split('|')[1])
					annotation = ('+').join(TF_list)
				elif TF_counter == 1:
					annotation = each_line[10].split(';')[0].split('=')[1].split('|')[1]
					if 'DBD-SUPERFAMILY' in annotation:
						annotation = annotation.split(',')[0]
				else:
					annotation = 'none'
				simplified_line.append(annotation)
			elif 'null' in each_line[1]:
				simplified_line[3] = each_line[10].split('=')[1]
				annotation = 'null'
				simplified_line.append(annotation)
			else:
				annotation = 'empty line'
				simplified_line.append(annotation)
			simplified_line = '\t'.join(simplified_line)

			with open(dir + "/cgc_standard.out", 'a') as f:
				f.write(simplified_line+'\n')
				f.close()
		else:
			pass
	


# if __name__ == "__main__":
#     cgc_file = sys.argv[1]
    
#     simplify_output(cgc_file)
