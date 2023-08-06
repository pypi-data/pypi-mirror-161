import json
import numpy as np
from sklearn import mixture

class MsaGmmAssessment():

    def gmm_generator(self, msa_filename, single_preds):
        data_full = []
        with open(msa_filename) as json_file:
            data = json.load(json_file)
            for aln_pos in range(len(data['results']['results']['backbone']['median'])):
                pred_vector = []
                for biophys in ['backbone', 'sidechain', 'coil', 'sheet', 'helix',
                     'earlyFolding', 'disoMine']:
                     pred_vector.append(
                        data['results']['results'][biophys]['median'][aln_pos])

                data_full.append(pred_vector)

        X_train = np.vstack(data_full)
        clf = mixture.GaussianMixture(n_components = 1, covariance_type = 'full',
                                      verbose = 2, verbose_interval = 1)
        clf.fit(X_train)

        gmm_dict = {}
        scores = []
        gmm_info = {}
        for prot in single_preds.keys():
            if prot != "sequence":
                full_pred = []
                for res in range(len(single_preds[prot]['backbone'])):
                    pred_vector = []
                    for biophys in ['backbone', 'sidechain', 'coil', 'sheet', 'helix',
                                    'earlyFolding', "disoMine"]:
                        if single_preds[prot][biophys][res] != None:
                            pred_vector.append(single_preds[prot][biophys][res])

                    full_pred.append(pred_vector)

                full_pred = [list for list in full_pred if list]

                preds = np.vstack(full_pred)
                gmm_info[prot] = clf.score_samples(preds).tolist()
                scores.extend(clf.score_samples(preds).tolist())

        perc_95 = np.percentile(scores, 5)
        perc_99 = np.percentile(scores, 1)
        perc_99_9 = np.percentile(scores, 0.1)

        for key in gmm_info.keys():
            perc_95_list = ["Out" if i <= perc_95 else "In" for i in gmm_info[key]]
            perc_99_list = ["Out" if i <= perc_99 else "In" for i in gmm_info[key]]
            perc_99_9_list = ["Out" if i <= perc_99_9 else "In" for i in gmm_info[key]]

            gmm_dict[key] = {"scores": gmm_info[key], "perc_95": perc_95_list,
                   "perc_99": perc_95_list, "perc_99_9": perc_99_9_list}

        with open('{}_quantification.json'.format(msa_filename.split(".")[0]), 'w') as fp:
            json.dump(gmm_dict, fp)
