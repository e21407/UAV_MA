import random
from itertools import product
from itertools import combinations
import operator
import math

class GeneralTool:
	def __init__(self, strProjectName):
		self.projectName = strProjectName
	# ================================================	
	def Get_a_decimal_number_by_a_given_lstBinaryNum( self, _input_lstBinaryNum ):
		if len(_input_lstBinaryNum)<=0:
			print('Error: Get_a_decimal_number_by_a_given_lstBinaryNum, len(_input_lstBinaryNum)<1.\n')#
			raw_input()			
		## --- 1 convert this list into str
		strBinaryNumber = ''.join( str(e) for e in _input_lstBinaryNum )#
		## --- 2 convert this str into the decimal number
		ret_decimal_num = int(strBinaryNumber,2)#
		return ret_decimal_num##EoF:~
	# ================================================	
	def Get_a_lstBinaryNumber_by_a_given_intDecimalNum( self, _input_intDecimalNum, LEN_binaryCode ):
		if _input_intDecimalNum<0 or LEN_binaryCode<=0:
			print('Error: Get_a_lstBinaryNumber_by_a_given_intDecimalNum, _input_intDecimalNum<0 or LEN_binaryCode<=0.\n')#
			raw_input()			
		## ===== 1 convert this int into strBinaryNum
		if 0==_input_intDecimalNum:
			strBinaryNum = ''.join('0' for i in range(int(LEN_binaryCode)))## !!!
		else:
			strBinaryNum = bin(_input_intDecimalNum)#
		
		## ===== 2 convert this strBinaryNum (e.g., '0b110') into the pre-defined-length list-binary-number.
		# print '_input_intDecimalNum: ',_input_intDecimalNum
		# print 'LEN_binaryCode: ',LEN_binaryCode
		# print 'strBinaryNum: ',strBinaryNum
		ret_lstBinaryNum = []
		#### ------ 2.1 partially copy the former severl bits before 'b'.
		for i in reversed(xrange(len(strBinaryNum))):#
			strBitVal_i = strBinaryNum[i]#
			# print 'strBitVal_i: ',strBitVal_i
			if 'b'==strBitVal_i:
				break##
			ret_lstBinaryNum.append( int( strBitVal_i ) )##
		#### ---- !!!! Revser it back to normal sequence:
		ret_lstBinaryNum.reverse()
		# print 'ret_lstBinaryNum 1 : ',ret_lstBinaryNum
		
		#### ------ 2.2 check the length and supplement the length of the ret_lstBinaryNum to the pre-defined length.
		if len(ret_lstBinaryNum)<LEN_binaryCode:
			len_prefix_supplemented = LEN_binaryCode - len(ret_lstBinaryNum)#
			for i in range(len_prefix_supplemented):
				ret_lstBinaryNum.insert(0, 0)#		
		# print 'ret_lstBinaryNum 2 : ',ret_lstBinaryNum
		# raw_input()
		return ret_lstBinaryNum##EoF:~
	# ================================================	
	def Get_ceil_num_of_binaryBits_of_an_integerNum(self, _input_intNum):
		if _input_intNum<=0:
			print('Error: Get_ceil_num_of_binaryBits_of_an_integerNum, _input_intNum<=0.\n')#
			raw_input()#	
		return int(math.ceil( math.log(_input_intNum, 2) ))##EoF:~
	# ================================================		
	def Get_a_random_binary_number(self):##
		return random.choice([0,1])##
	# ================================================
	def Get_a_random_int_number_within_a_range(self, lb,ub):
		ret_num = -1#
		if lb <= ub:
			ret_num = random.randint(lb, ub)#
		return ret_num## EoF:~
	# ================================================
	def Get_a_random_real_number_within_a_range(self, lb,ub):
		ret_num = -1#
		if lb==ub:
			return lb##
		if lb < ub:
			ret_num = random.uniform(lb, ub)#
		return ret_num## EoF:~	
	# ================================================
	# return a random element from the given list.
	def Get_a_random_element_from_a_list( self, input_list ):
		size_of_list = len(input_list)#
		if size_of_list<1:
			print('Error: Get_a_random_element_from_a_list, size_of_list<1.\n')#
			raw_input()
		
		## --- normal routine:
		idx_target=0##
		if 1<size_of_list:
			idx_target = random.randint(0,size_of_list-1);
		ret_rdm_element = input_list[idx_target];
		return ret_rdm_element## EoF:~
	# ================================================
	def copy_a_lstPart_from_a_list(self, input_list, _pos_idx_beg, _pos_idx_end):
		size_of_list = len(input_list)#
		if size_of_list<1 or _pos_idx_beg <0 or _pos_idx_end >= size_of_list:
			print('Error: copy_a_lstPart_from_a_list, len(input_list)<1 or _pos_idx_beg <0 or _pos_idx_end >= size_of_list.\n')#
			raw_input()#
		if _pos_idx_beg > _pos_idx_end:
			print('Error: copy_a_lstPart_from_a_list, _pos_idx_beg > _pos_idx_end.\n')#
			raw_input()#
		## --- normal routine:
		ret_lstPart = []
		for idx_to_copy in range(_pos_idx_beg, _pos_idx_end+1):
			element = input_list[idx_to_copy]
			ret_lstPart.append(element)#
		return ret_lstPart### EoF :~
	# ================================================
	def Get_a_number_of_random_samples_from_a_list(self, input_list, num_sample):
		size_of_list = len(input_list)#
		if size_of_list<1:
			print('Error: Get_a_number_of_random_samples_from_a_list, len(input_list)<1.\n')#
			return []#
		if num_sample > size_of_list:
			print('Error: Get_a_number_of_random_samples_from_a_list, num_sample > len(input_list).\n')#
			return []#
		## --- normal routine:
		return random.sample(input_list, num_sample)#
	# ================================================
	def Whether_an_element_in_a_given_list( self, element, lst ):
		if element in lst:
			return 1#
		else:
			return 0##EoF:~
	# ==========================================================================================
	def Get_lst_of_keys_from_a_given_dict( self, dct_input ):
		return dct_input.keys()## EoF:~
	# ================================================
	def Get_the_key_with_max_value_of_a_dict( self, dct_input ):
		return max(dct_input.iteritems(), key=operator.itemgetter(1))[0]## EoF:~
	# ================================================
	def Get_max_value_of_a_dict( self, dct_input ):
		dictTemp={v:k for k,v in dct_input.items()}
		return dct_input[ dictTemp[max(dictTemp)] ]
	# ================================================
	def Get_min_value_of_a_dict( self, dct_input ):
		dictTemp={v:k for k,v in dct_input.items()}
		return dct_input[ dictTemp[min(dictTemp)] ]
	# ================================================		
	def Get_all_products_from_a_list( self, lst_ele, length ):
		if (length> len(lst_ele) ):
			return []
		ret_list = []
		middle_list = list( product(lst_ele, repeat = length) )
		## --- filter the repeated elements
		for it in middle_list:
			if len(it) == len(set(it)):
				ret_list.append( it )
		return ret_list## EoF:~
	# ================================================		
	def Get_all_combinations_from_a_list( self, lst_ele, length ):
		if (length> len(lst_ele) ):
			return []
		ret_list = list( combinations(lst_ele, length) )
		return ret_list## EoF:~
	# ================================================	