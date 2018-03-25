import random


class SimulateTime:
	m_dCurrentTime = 0.0#
	m_gcdTimeStep = 0.0#
	m_nCurrent_ts_idx = 0##

	def __init__(self, NS_STEP_TICK_inSec, NS_SPEED_RATIO=1.0):
		self.m_gcdTimeStep = NS_STEP_TICK_inSec * NS_SPEED_RATIO## EoF:~
	# ================================================
	def TimeStepForward( self ):
		##LogicalTime steps forward  dStep_second ms, every step.
		self.m_dCurrentTime += self.m_gcdTimeStep##
		self.m_nCurrent_ts_idx += 1## EoF:~
	# ================================================
	def Get_CurrentTime( self ):
		return self.m_dCurrentTime## EoF:~
	# ================================================
	def Get_current_ts_idx( self ):
		return self.m_nCurrent_ts_idx## EoF:~
	# ================================================
	def Reset_NS_time( self ):
		self.m_dCurrentTime = 0.0## EoF:~
	# ================================================
	def Get_length_of_timeSlot( self ):
		return self.m_gcdTimeStep## EoF:~
	# ================================================