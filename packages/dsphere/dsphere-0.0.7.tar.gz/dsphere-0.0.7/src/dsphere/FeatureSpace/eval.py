import numpy as np
from sklearn.metrics import accuracy_score, f1_score, log_loss, precision_score, recall_score, mean_squared_error, confusion_matrix
import warnings

def _multiclass_scores_at_k(actual, preds, probs, k, average_type):
      
    probs_sort_order = np.argsort(probs)

    actual_ordered = actual[probs_sort_order]
    actual_ordered = actual_ordered[len(actual_ordered)-k-1:]
    preds_ordered = preds[probs_sort_order]
    preds_ordered = preds_ordered[len(preds_ordered)-k-1:]
    
    # TODO: Multiclass recall_k and f1_k need to be fixed
    accuracy_k = accuracy_score(actual_ordered, preds_ordered)
    f1_k = f1_score(actual_ordered, preds_ordered, average=average_type)
    precision_k = precision_score(actual_ordered, preds_ordered, average=average_type)
    recall_k = recall_score(actual_ordered, preds_ordered, average=average_type)
    high_value_preds_k = np.sum(preds_ordered > 1)
    #log_loss_k = log_loss(actual_ordered, preds_ordered)
    
    return accuracy_k, f1_k, precision_k, recall_k, high_value_preds_k


def eval_multiclass_scores(actual, preds, probs, k, average_type):
    
    accuracy = accuracy_score(actual, preds)    
    f1 = f1_score(actual, preds,average=average_type)
    precision = precision_score(actual, preds, average=average_type)
    recall = recall_score(actual, preds, average=average_type)
    high_value_preds = np.sum(preds > 1)
    #log_loss_tot = log_loss(actual, preds)
    rmse = np.sqrt(mean_squared_error(actual, probs[:,1]))
    matrix = confusion_matrix(actual, preds)
    
    accuracy_k, f1_k, precision_k, recall_k, high_value_preds_k = _multiclass_scores_at_k(actual, preds, probs[:,1], k)

    return {'accuracy':accuracy,
            'accuracy_k':accuracy_k,
            'f1':f1,
            'f1_k':f1_k,
            'precision':precision,
            'precision_k':precision_k,
            'recall':recall,
            'recall_k':recall_k,
            #'value':value,
            #'value_k':value_k,
            'high_value_preds':high_value_preds,
            'high_value_preds_k':high_value_preds_k,
            #'log_loss':log_loss_tot,
            #'log_loss_k':log_loss_k,
            'rmse':rmse,
            'matrix':matrix}

def _binary_scores_at_k(actual, preds, probs, k):
    tn, fp, fn, tp = confusion_matrix(actual, preds, labels=[0,1]).ravel()
    
    probs_sort_order = np.argsort(probs)

    actual_ordered = actual[probs_sort_order]
    actual_ordered = actual_ordered[len(actual_ordered)-k-1:]
    preds_ordered = preds[probs_sort_order]
    preds_ordered = preds_ordered[len(preds_ordered)-k-1:]
    
    tn_k, fp_k, fn_k, tp_k = confusion_matrix(actual_ordered, preds_ordered, labels=[0,1]).ravel()

    accuracy_k = accuracy_score(actual_ordered, preds_ordered)
    recall_k = tp_k / (tp + fn)
    
    if ((tp_k + fp_k) == 0):
        precision_k = 0
        warnings.warn("_binary_scores_at_k(): Precision is ill-defined and being set to 0.0 due to no predicted samples")
    else:
        precision_k = tp_k / (tp_k + fp_k)
        
    #log_loss_k = log_loss(actual_ordered, preds_ordered)
    
    if ((precision_k + recall_k) == 0):
        f1_k = 0
        warnings.warn("_binary_scores_at_k(): F-score is ill-defined and being set to 0.0 due to no predicted samples")
    else:
        f1_k = (2 * (precision_k * recall_k)) / (precision_k + recall_k)
    
    return accuracy_k, f1_k, precision_k, recall_k


def eval_binary_scores(actual, preds, probs, k):
    
    accuracy = accuracy_score(actual, preds)
    f1 = f1_score(actual, preds)
    print("actual:", actual.shape, type(actual))
    print("preds:", preds.shape, type(preds))
    precision = precision_score(actual, preds)
    recall = recall_score(actual, preds)
    #log_loss_tot = log_loss(actual, preds)
    rmse = np.sqrt(np.mean(np.square(probs - actual), axis=-1))
    #rmse = np.sqrt(mean_squared_error(actual, probs[:,1]))
    matrix = confusion_matrix(actual, preds)
    num_1s = preds.sum()
    num_rows = preds.shape[0]
    
    accuracy_k, f1_k, precision_k, recall_k = _binary_scores_at_k(actual, preds, probs, k)
    # Andrew change
    #accuracy_k, f1_k, precision_k, recall_k = _binary_scores_at_k(actual, preds, probs[:,1], k)

    #TODO: Add sklearn.metrics.roc_auc_score
    
    return {'accuracy':accuracy,
            'accuracy_k':accuracy_k,
            'f1':f1,
            'f1_k':f1_k,
            'precision':precision,
            'precision_k':precision_k,
            'recall':recall,
            'recall_k':recall_k,
            'num_1s':num_1s,
            'num_rows': num_rows,
            #'log_loss':log_loss_tot,
            #'log_loss_k':log_loss_k,
            'rmse':rmse,
            'matrix':matrix}