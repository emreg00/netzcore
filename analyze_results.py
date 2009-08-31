#########################################################################
# Methods for analyzing output files from scoring methods
#
# eg 13/08/2009
#########################################################################

from biana.utilities import graph_utilities as network_utilities

#def generate_xval_ROCR_files():
#    return

def create_R_script(fileName):
    f = open(fileName, "w")
    f.write("library(ROCR)\n\n") 
    f.write("v<-read.table(\"predictions.txt\")\n") 
    f.write("l<-read.table(\"labels.txt\")\n")
    f.write("pred<-prediction(v, l)\n")
    f.write("postscript(\"performance.eps\", width = 6, height = 6, horizontal = FALSE, onefile = FALSE, paper = \"special\")\n")
    f.write("par(mfrow=c(2,2))\n")
    f.write("perfROC<-performance(pred, \"tpr\", \"fpr\")\n")
    f.write("plot(perfROC, lwd=2, col=2, xlab=\"FPR\", ylab=\"TPR\", main=\"ROC curve (averaged over xval folds)\", plotCI.col=2, avg=\"vertical\", spread.estimate=\"stddev\", show.spread.at=seq(0,1,by=0.20))\n")
    #f.write("title(\"ROC\")\n")
    f.write("legend(\"topright\", c(\"Scoring\"), lty=c(1), col=c(2))\n") 
    f.write("perfPPV<-performance(pred, \"ppv\")\n")
    f.write("perfSens<-performance(pred, \"sens\")\n")
    f.write("plot(perfPPV, lwd=2, col=2, ylab=\"PPV/Sens\", main=\"PPV vs Sensitivity (averaged over xval folds)\", plotCI.col=2, avg=\"vertical\", spread.estimate=\"stddev\", show.spread.at=seq(0,1,by=0.20))\n")        
    f.write("plot(perfSens, lwd=2, col=3, plotCI.col=3, avg=\"vertical\", spread.estimate=\"stddev\", show.spread.at=seq(0,1,by=0.15), add=TRUE)\n") 
    f.write("legend(\"bottomright\", c(\"PPV\", \"Sens\"), lty=c(1,1), col=c(2,3))\n") 
    f.write("perfAUC<-performance(pred, \"auc\")\n")
    f.write("e=c(); n=c(); x=0; for ( i in perfAUC@y.values ) { x<-x+1;  e[x] <- i; n[x]<-x }; barplot(e, names=n, ylim=c(0,1),ylab= \"AUC\",xlab=\"Fold\", main=\"Area under ROC curve (AUC)\")\n")
    f.write("legend(\"topright\", c(paste(\"(Avg: \", mean(e), \")\",sep=\"\")), lty=c(), col=c())\n") 
    f.write("perfRMSE<-performance(pred, \"rmse\")\n")
    f.write("e=c(); n=c(); x=0; for ( i in perfRMSE@y.values ) { x<-x+1;  e[x] <- i; n[x]<-x }; barplot(e, names=n, ylim=c(0,1),ylab= \"RMSE\",xlab=\"Fold\"); title(\"Root mean square error (RMSE)\")\n")
    f.write("legend(\"topright\", c(paste(\"(Avg: \", mean(e), \")\", sep=\"\")), lty=c(), col=c())\n") 
    f.write("dev.off()\n")
    f.close()
    #os.system("R CMD BATCH %s" % "*.R") 
    return

def create_ROCR_files(list_node_scores_and_labels, file_predictions, file_labels):
    """
	list_node_scores_and_labels: list of node (score, label) tuple (corresponding to each validation node) list (corresponding to xval fold)
    """
    fileOut = open(file_predictions, 'w')
    fileOut2 = open(file_labels, 'w')
    firstTime = True
    for i, node_scores_and_labels in enumerate(zip(*list_node_scores_and_labels)):
	if i == 0:
            for j in xrange(len(node_scores_and_labels)):
                fileOut.write("\tFold_" + str(j+1))  
                fileOut2.write("\tFold_" + str(j+1))  
            fileOut.write("\n")  
            fileOut2.write("\n")  
        fileOut.write("%d"%i)
        fileOut2.write("%d"%i)
        for (score, label) in node_scores_and_labels:
            fileOut.write("\t" + str(score))
            fileOut2.write("\t" + str(label))
        fileOut.write("\n")
        fileOut2.write("\n")
    fileOut.close()
    fileOut2.close()
    return


def get_validation_node_scores_and_labels(file_result, file_seed_test_scores, file_node_scores, n_random_negative_folds = 1):
    setNodeResult, setDummy, dictNodeResult, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_result, store_edge_type = False)
    setNodeTest, setDummy, dictNodeTest, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_seed_test_scores, store_edge_type = False)
    non_seeds = get_non_seeds_from_node_scores_file(file_node_scores, default_score = 0)
    #node_to_validation_data = dict([ (id, (dictNodeResult[id], 1)) for id in setNodeTest ])
    node_validation_data = [ (dictNodeResult[id], 1) for id in setNodeTest ]

    n_actual_folds = 0
    negative_scores = [ 0 ] * len(setNodeTest)
    for sample in generate_samples_from_list_without_replacement(non_seeds, len(setNodeTest), n_random_negative_folds):
	for i, id in enumerate(sample):
	    negative_scores[i] += dictNodeResult[id] 
	n_actual_folds += 1
    node_validation_data.extend(map(lambda x: (x/n_actual_folds, 0), negative_scores))
    return node_validation_data


def generate_samples_from_list_without_replacement(elements, sample_size, n_folds):
    from random import shuffle
    shuffle(elements)
    for i in range(n_folds):
	if (i+1)*sample_size < len(elements):
	    yield elements[i*sample_size:(i+1)*sample_size]
    return


def get_non_seeds_from_node_scores_file(file_node_scores, default_score = 0):
    """
	file_node_scores: initial node/seed scores
    """
    setNode, setDummy, dictNode, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_node_scores, store_edge_type = False)
    non_seeds = [ id for id, score in dictNode.iteritems() if score > default_score ]
    return non_seeds


def calculate_performance_metric_counts(file_result, file_seed_test_scores, file_node_scores, score_threshold, n_random_negative_folds = 1, default_score = 0):
    """
	Calculate and return TP, FP, TN, FN (FP and TN based on random selected non-seed nodes)
	file_result: output scores file
	file_seed_test_scores: seed nodes separated for test
	file_node_scores: initial node/seed scores
	score_threshold: threshold for considering data as P, N
	n_random_negative_folds: Number of negative data selection folds (each fold contain same number of test nodes) to be averaged for FP and TN calculation. FP and TN are not necesserily integers when n_random_negative_folds > 1
    """
    setNodeResult, setDummy, dictNodeResult, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_result, store_edge_type = False)
    setNodeTest, setDummy, dictNodeTest, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_seed_test_scores, store_edge_type = False)
    non_seeds = get_non_seeds_from_node_scores_file(file_node_scores, default_score = 0)

    (nTP, nFP, nFN, nTN) = (0.0, 0.0, 0.0, 0.0)
    for id, score in dictNodeResult.iteritems():
        if id in setNodeTest:
            if score >= score_threshold:
                nTP += 1
            else:
                nFN += 1

    n_actual_folds = 0
    for sample in generate_samples_from_list_without_replacement(non_seeds, len(setNodeTest), n_random_negative_folds):
	setNegative = set(sample)
	n_actual_folds += 1
	for id, score in dictNodeResult.iteritems():
	    if id in setNegative:
		if score >= score_threshold:
		    nFP += 1
		else:
		    nTN += 1
    nFP /= n_actual_folds
    nTN /= n_actual_folds
    return (nTP, nFP, nFN, nTN)


def calculatePerformance(nTP, nFP, nFN, nTN):
    acc = (nTP + nTN) / (nTP + nFP + nTN + nFN)
    try:
        sens = nTP / (nTP + nFN)
    except:
        sens = None
    try:
        spec = nTN / (nTN + nFP)
    except:
        spec = None
    try:
        ppv = nTP / (nTP + nFP)
    except:
        ppv = None

    #if spec is not None:
    #    return (sens, (1-spec))
    #else:
    #    return (sens, None)

    return (acc, sens, spec, ppv)


def calculate_seed_coverage_at_given_percentage(file_result, file_seed_scores, percentage, default_score=0):
    """
	Calculates number of seed nodes included in the given percentage of high ranking nodes in result file 
	Returns a tuple containing number of seed nodes and all nodes at that percentage
    """
    setDummy, setDummy, dictNodeResult, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_result, store_edge_type = False)
    setDummy, setDummy, dictNode, dictDummy = network_utilities.get_nodes_and_edges_from_sif_file(file_name = file_seed_scores, store_edge_type = False)
    
    result_scores = dictNodeResult.items()
    result_scores.sort(lambda x,y: cmp(y[1], x[1]))

    i = 0
    n = len(result_scores)*percentage/100
    n_seed = 0
    
    last_score = result_scores[0][1]
    for id, score in result_scores:
	i+=1
	if i>n:
	    if last_score != score:
		#print "i,n:", i, n
		#print "id,score,last:", id, score, last_score
		break
	# checking whether node was a seed (using initial non-seed score assumption)
	if dictNode.has_key(id) and dictNode[id] > default_score:
	    n_seed += 1
	last_score = score
    
    return n_seed, n, i

