import json
import numpy as np
# import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Call the function below to plot the results
# self.plot_results(json_file_names, mutation)



class Plotter:
	def __init__(self):
		self.biophys_dict = {1: 'backbone', 2: 'sidechain', 3: 'coil',
							 4: 'sheet', 5: 'helix', 6: 'earlyFolding',
							 7: 'disoMine'}

	def plot_msa_distrib(self, jsondata_list, mutation=False):
		colors = ['blue', 'orange']
		opt = int(input('Show plots or save the images?\n'
						'(0 = show; 1 = save)>>>'))
		# These for loops got too complicated, I have to think
		# something simpler to handle the None values in the data
		for biophys_data in jsondata_list[0]["results"].keys():
			for data, col in zip(jsondata_list, colors):
				none_idx = []
				for n in range(len(data['results'][biophys_data]['median'])):
					if data['results'][biophys_data]['median'][n] == None \
							or data['results'][biophys_data][
						'firstQuartile'][n] == None \
							or data['results'][biophys_data][
						'thirdQuartile'][n] == None:
						none_idx.append(n)

				range_list = []
				for n in range(len(none_idx)):
					try:
						if none_idx[n] + 1 != none_idx[n + 1]:
							range_list.append(
								(none_idx[n] + 1, none_idx[n + 1]))
						else:
							continue
					except:
						if len(none_idx) == 1:
							range_list.append((0, none_idx[0]))
							range_list.append((none_idx[0] + 1, len(
								data['results'][biophys_data][
									'median'])))

						else:
							range_list.append((0, none_idx[0]))
							range_list.append((none_idx[-1] + 1, len(
								data['results'][biophys_data][
									'median'])))

				# When there are None values in the data
				if range_list:
					for tuple in range_list:
						x = np.arange(tuple[0], tuple[1], 1)
						firstq = \
							data['results'][biophys_data][
								'firstQuartile'][
							tuple[0]:tuple[1]]
						thirdq = \
							data['results'][biophys_data][
								'thirdQuartile'][
							tuple[0]:tuple[1]]
						bottom = \
							data['results'][biophys_data][
								'bottomOutlier'][
							tuple[0]:tuple[1]]
						top = \
							data['results'][biophys_data]['topOutlier'][
							tuple[0]:tuple[1]]
						plt.fill_between(
							x, firstq, thirdq, alpha=0.5, color=col)
						plt.fill_between(
							x, bottom, top, alpha=0.25, color=col)

				# When there aren't None values in the data
				else:
					x = np.arange(0, len(
						data['results'][biophys_data]['median']), 1)
					firstq = data['results'][biophys_data][
						'firstQuartile']
					thirdq = data['results'][biophys_data][
						'thirdQuartile']
					bottom = data['results'][biophys_data][
						'bottomOutlier']
					top = data['results'][biophys_data]['topOutlier']
					plt.fill_between(
						x, firstq, thirdq, alpha=0.5, color=col)
					plt.fill_between(
						x, bottom, top, alpha=0.25, color=col)

				plt.plot(data['results'][biophys_data]['median'],
						 linewidth=1, color=col)

				if mutation:
					print(mutation)
					plt.plot(mutation['results'][biophys_data],
							 linewidth=0.5, color='red')

			plt.axis(
				[0, len(data['results'][biophys_data]['median']), 0, 1.1])
			plt.ylabel(biophys_data)
			plt.xlabel('Residue position')

			# if opt == 0:
			plt.show()
			# if opt == 1:
			# 	filename = file.split('.')[0] + '_' + biophys_data + '.png'
			# 	plt.savefig(filename)
			# 	print(
			# 		'plot succesfully saved in results/{}'.format(filename))
			# 	plt.close()

	def plot_json(self, jsondata):
		opt = int(input('Show plots or save the images?\n'
						'(0 = show; 1 = save)>>>'))

		for biophys_data in jsondata[list(jsondata.keys())[0]].keys():
			for result_id in jsondata.keys():
				if result_id != "sequence":
					plt.plot(jsondata[result_id][biophys_data],
							 label=result_id)
					plt.legend()
					plt.title(result_id)
					plt.ylabel(biophys_data)
					plt.xlabel('Residue position')

			# if opt == 0:
			plt.show()

			# if opt == 1:
			# 	filename = json_file_names.split(".")[
			# 				   0] + '_' + biophys_data + '.png'
			# 	plt.savefig("results/" + filename)
			# 	print('plot succesfully saved in results/{}'.format(filename))
			# 	plt.close()

		def plot_sinlge_seq(json_file_names, msa_like, mutation):
			with open(json_file_names) as json_file:
				data = json.load(json_file)
				opt = int(input('Show plots or save the images?\n'
							  '(0 = show; 1 = save)>>>'))

				for result_id in data['results']:
					for biophys_data in self.biophys_dict.values():
						plt.plot(result_id[biophys_data], label = result_id['proteinID'])
						plt.legend()
						plt.title(data['id'])

						plt.ylabel(biophys_data)
						plt.xlabel('Residue position')

						if opt == 0:
							plt.show()

						if opt == 1:
							filename = result_id['proteinID'] + '_' + biophys_data + '.png'
							plt.savefig("results/" + filename)
							print('plot succesfully saved in results/{}'.format(filename))
							plt.close()
