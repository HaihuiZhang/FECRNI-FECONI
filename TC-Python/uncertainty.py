from tc_python import *
"""
This example shows how to create a single equilibrium calculation                
from a ternary system and configure it to calculate the solidus 
and liquidus temperature using fixed phase conditions for the 
liquid phase. 

There can be multiple solutions to a fixed phase condition and it is 
good practice to perform a regular equilibrium calculation close to 
where the phase transition is. This example starts with an equilibrium 
calculation at 1700K in order to get good start values.           
"""


def list_stable_phases(calc_result):
    """
    List the stable phases and their amount on screen.

    Args:
        calc_result: Calculation result from an equilibrium calculation
    """
    stable_phases = calc_result.get_stable_phases()
    for phase in stable_phases:
        print("Amount of " + phase + " = {0:.3f}".format(calc_result.get_value_of('NP(' + phase + ')')))

import pandas as pd
df = pd.read_excel('phasepoints.xlsx', header=None)
mole_fraction_of_a_component_Ni_array = df.iloc[:, 0].values
mole_fraction_of_a_component_Fe_array = df.iloc[:, 1].values
j_count = df.shape[0]
final_dfs = []
for j in range(j_count):
	stable_phases_dict = {}
	with TCPython() as session:
		for i in range(2, 501):
			print(i)
			eq_calculation = (
				session.
				select_user_database_and_elements(r"D:/tdbset/{}.tdb".format(i), ["Fe", "Cr", "Ni"]).
				get_system().
				with_single_equilibrium_calculation().
				set_condition(ThermodynamicQuantity.temperature(), 973.0).
				set_condition(ThermodynamicQuantity.mole_fraction_of_a_component("Ni"), mole_fraction_of_a_component_Ni_array[j]).
				set_condition(ThermodynamicQuantity.mole_fraction_of_a_component("Fe"), mole_fraction_of_a_component_Fe_array[j])
			)
			calc_result = eq_calculation.calculate()
			stable_phases = calc_result.get_stable_phases()
			phases_str = "-".join(sorted(stable_phases))
			print(phases_str)
			if phases_str in stable_phases_dict:
				stable_phases_dict[phases_str] += 1
			else:
				stable_phases_dict[phases_str] = 1
	df = pd.DataFrame(list(stable_phases_dict.items()), columns=['stable_phases', 'count'])
	df['j'] = j + 1
	final_dfs.append(df)
final_df = pd.concat(final_dfs, keys=range(1, j_count+1), axis=0)
final_df = final_df.pivot_table(index='stable_phases', columns='j', values='count', fill_value=0)
final_df = final_df.reset_index()
final_df.to_excel('stable_phases_count_all.xlsx', index=False)