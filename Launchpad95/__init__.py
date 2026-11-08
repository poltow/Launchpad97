from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad import Launchpad

def create_instance(c_instance):
	""" Creates and returns the Launchpad script """
	return Launchpad(c_instance)

def get_capabilities():
	return {
		CONTROLLER_ID_KEY: controller_id(
			vendor_id = 4661, 
			# USB product ids of the legacy (non RGB) Launchpad family:
			# 14 = Launchpad (original), 32 = Launchpad S, 54 = Launchpad Mini MK1
			product_ids = [14, 32, 54],
			model_name =
			[
				'Launchpad',
				'Launchpad S',
				'Launchpad Mini'
			]
		),
		PORTS_KEY: 
			[
				inport(props = [NOTES_CC, SCRIPT, REMOTE]), 
				outport(props = [NOTES_CC, SCRIPT, SYNC, REMOTE])
			]
	}
