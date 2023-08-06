class mustafa:
    alldict = dict()
    dictclasses = dict()
    trainings = dict()
    latesttraining = dict()
    modelsorder = dict()
    precision = 1
    maxattrs = "max"
    selection = []
    votingalgos = dict()
    atype = ""
    parameters = 0
    stats = None
    def __init__(m, precision=1, maxattrs="max",atype="",selection=[],hyperstep=1,stats=False):
        dictionaries = dict()
        import sklearn
        import inspect
        import sklearn.svm , sklearn.neural_network , sklearn.tree , sklearn.neighbors , sklearn.naive_bayes , sklearn.ensemble
        import re
        m.precision = precision
        #print(precision)
        m.maxattrs = maxattrs
        m.atype = atype
        m.selection = selection
        m.alldict = dict()
        m.dictclasses = dict()
        m.stats = stats
        #print(precision,atype,maxattrs,selection)
        categories = [sklearn.svm,sklearn.neural_network,sklearn.tree,sklearn.neighbors,sklearn.naive_bayes,sklearn.ensemble]
        
        m.parameters = 0
        for category in categories:
            models = []
            for k, v in enumerate(dir(category)):
                if "_" not in v:
                    ex_locals = {}
                    exec("from {0} import {1};model = {1}".format(str(category.__name__),str(v)), None, ex_locals)
                    model = ex_locals['model']
                    firstline = str(model.__doc__).split("\n")[0]
                    #print(firstline)
                    atype1 = ""
                    #print(m.atype)
                    if m.atype.lower() in "classification":
                        atype1 = "classifier"
                        #print(m.atype)
                        #print(atype1)
                    if m.atype.lower() in "regression":
                        atype1 = "regressor"
                        #print(m.atype)
                        #print(atype1)
                    if m.atype in firstline.lower() or atype1 in firstline.lower():
                        try:
                            if model.__doc__ == None:
                                continue
                            if "Warning" in model.__doc__:
                                continue
                            if len(model.__doc__) < 100:
                                continue
                            s = model

                            a = re.search(r'\b(Parameters)\b', s.__doc__)
                            b = re.search(r'\b(Attributes)\b', s.__doc__)
                            a.start()
                            b.start()
                        except:
                            continue
                        modelname = str(s.__name__)
                        
                        votingalgo = False
                        try:
                            sigi = str(inspect.signature(s))
                            if "estimators" in sigi and "n_estimators" not in sigi:
                                votingalgo = True
                        except:
                            pass
                        if len(m.selection) > 0 and not votingalgo:
                            if modelname not in m.selection:
                                continue
                        #print(modelname)
                        #print(firstline)
                        params = s.__doc__[ a.start() + len("parameters") : b.start() ]

                        def convert_data(values, default,prec):
                            if "{" in str(default) and "}" in str(default):
                                return default        
                            if values == "int":# and dataType(str(default)) == "INT":
                                if int(prec) <= 1:
                                    #if values == "None":
                                    #    return "deny"
                                    if str(default)[1:-2].isalpha():
                                        return [default]
                                    return [int(default)]
                                multi = False
                                if default == "None" or str(default)[1:-2].isalpha():
                                    default = 10
                                if float(default) < 0.0:
                                    return [int(default)]
                                ilist = []
                                if float(default) > 0.0 and float(default) < 1.0:
                                    multi = True 
                                if float(default) == 0.0:
                                    default = 1
                                    ilist.append(0.0)
                                drange = int(float(default)/2.0)
                                default = int(default)
                                ilist.append(default)
                                if multi:
                                    for x in range(1,prec+1):
                                        if multi:
                                            ilist.append(default*drange*x)
                                    return ilist
                                
                                val = default
                                finallist = [val]
                                step = int(val*0.25*hyperstep)
                                if step == 0:
                                    step = 1
                                upper = [element for element in range(val, int(val*prec)-1, step)]
                                lower = [element for element in range(val, 0, -step)]
                                for x in range(1,round(prec)-2):
                                    finallist.append(upper[x])
                                for x in range(1,abs(len(lower))):
                                    finallist.append(lower[x])
                                return finallist
                            
                            if values == "float":
                                if default == "None":
                                    default = 1.0
                                if int(prec) <= 1:
                                    return [float(default)]
                                if float(default) < 0.0:
                                    return [float(default)]
                                ilist = []
                                if float(default) == 0.0:
                                    default = 1
                                    ilist.append(0.0)
                                drange = float(default)/2.0
                                default = float(default)
                                for x in range(1,prec+1):
                                    if default*drange*x > 1000.0:
                                        ilist.append(default)
                                        return ilist
                                    ilist.append(default*drange*x)
                                return ilist
                            if values == "bool":
                                return [True,False]
                            if type(values) == list:
                                return values
                            if "int" in values:
                                #print("made it")
                                return convert_data("int",10,prec)
                            if "float" in values:
                                return convert_data("float",1.0,prec)
                            if 'str' in values and default != None:
                                return [default,None]
                            return "deny"


                        #lstart 
                        #lend = re.search(r'\n', params[1:]).start()
                        attrcounter = 0
                        hyperdict = dict()
                        for line in params[16:].split("\n"):
                            if "default=" in line and "verbose" not in line and "max_features" not in line:
                                sp = line.rfind(",")
                                #line = line.lstrip(' ')
                                #line = line.rstrip(' ')
                                #print(line)
                                l1 = line[:sp].split(":")
                                l2 = line[sp:].split("=")
                                name = l1[0].replace(" ",'')
                                if name == "n_jobs":
                                    hyperdict[name] = [-1]
                                    break
                                values = l1[1].replace(" ",'')
                                #print(values)
                                default = l2[len(l2)-1].replace(" ",'')
                                if "{" in values and "or" in values:
                                    values = values[values.find("{"):values.find("}")]
                                    
                                #print(values)
                                if "{" in values:
                                    values = values[1:-1].split(",")
                                    for i,value in enumerate(values):   
                                        value = value.replace('"','')
                                        value = value.replace("'",'')
                                        #print(value,1000)
                                        specialindex = -1
                                        replacelist1 = ["'",'"',"{","}",' ']
                                        #print(value)
                                        for key in replacelist1:
                                            if key in value:
                                                msp = value.find(key)
                                                value = value[:msp]
                                            if value == 'dict':
                                                specialindex = i
                                            values[i] = value
                                        if specialindex != -1:
                                            values[specialindex] = None

                                if type(maxattrs) == int:
                                    if attrcounter > maxattrs:
                                        break
                                    attrcounter = attrcounter + 1

                                values = convert_data(values,default,precision)
                                if values == "deny":
                                    #print(before, default, s)
                                    #print()
                                    continue
                                m.parameters = m.parameters + 1
                                hyperdict[name] = values
                                #print(modelname)
                                m.dictclasses[modelname] = category.__name__.split(".")[1]
                                #print(name,values,default)
                        #print(hyperdict)
                        for value in hyperdict.keys():
                            newlist = []
                            if None in hyperdict[value]:
                                for i,lv in enumerate(hyperdict[value]):
                                    if lv != None:
                                        lv = lv.replace('"','')
                                        lv = lv.replace("'",'')
                                        newlist.append(lv)
                                newlist.append(None)
                                hyperdict[value] = newlist
                                
                        if votingalgo:
                            #hyperdict['estimators'] = []
                            m.votingalgos[s] = hyperdict
                        else:
                            m.alldict[s] = hyperdict
                        
                        #m.listall(p=True)
        #print(m.parameters)
        m.listall(p=True)
        print()
        if m.stats:
            print("Thank you for opting in to share your results to improve {mustafa} :)")
        else:
            print("Feel free to share your training results to improve {mustafa} by setting (stats=True) in the constructor :)")



    def listall(m,p=False):
        names = []
        for k,v in enumerate(m.alldict):
            names.append(v.__name__)
        if p:
            print(names)
        else:
            return names
    # def names(m):
    #     names = dict()
    #     for k,v in enumerate(m.alldict):
    #         names[v.__name__] = m.alldict[v]
    #     return names
    def hypers(m):
        return m.alldict
    def hy(m):
        return m.dictclasses
    def attrs(m):
        return 'mustafa(precision=1, maxattrs="max",atype="",selection=[])'
    def select(m,s):
        m.__init__(selection=s)
        #return m.listall()
    def gridsearch(m,X,y,splits=2,estimate=1):
        
        gridsearches = dict()
        from sklearn.model_selection import train_test_split,GridSearchCV, StratifiedKFold
        from sklearn.model_selection import cross_val_score, cross_val_predict
        kf = StratifiedKFold(n_splits=splits)
        from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve, cohen_kappa_score, f1_score, recall_score, precision_score
        import datetime
        if estimate != 1:
            oldx = X
            X, _, y, _ = train_test_split(X, y, train_size=estimate, random_state=42)
            print("Estimating on ",round(len(oldx)*estimate),"(",estimate*100,"%) records out of ",len(oldx))
        def measures(predicted, y_test):
            print()
            metrics = dict()
            accuracy = accuracy_score(y_test, predicted)
            metrics["accuracy"] = accuracy
            print('Accuracy: %f' % accuracy)
            precision = precision_score(y_test, predicted)
            metrics["precision"] = precision
            print('Precision: %f' % precision)
            recall = recall_score(y_test, predicted)
            metrics["recall"] = recall
            print('Recall: %f' % recall)
            f1 = f1_score(y_test, predicted)
            metrics["f1"] = f1
            print('F1 score: %f' % f1)
            matrix = confusion_matrix(y_test, predicted)
            metrics["matrix"] = matrix
            print('Confusion Matrix')
            print(matrix)
            print()
            return metrics
        votingnames = []
        for algoname in list(m.votingalgos.keys()):
            votingnames.append(algoname.__name__)
        for k,v in enumerate(m.dictclasses):
            #from foo.bar import foo2
            try:
                import sklearn
                import importlib
                if v in votingnames:
                    continue
                print(m.dictclasses[v],v)
                model = getattr(importlib.import_module(f"sklearn.{m.dictclasses[v]}"), v)

                etc = model()
                modelname = model.__name__
                print(model)
                etc_search_param= m.alldict[model]
                model_GS = GridSearchCV(estimator=etc,
                                     param_grid = etc_search_param,
                                     scoring=["accuracy", "recall"],
                                     refit="accuracy",
                                     verbose= -1,
                                     cv=kf,
                                     n_jobs=-1)
                time1 = datetime.datetime.now()
                model_GS.fit(X, y)
                model = model_GS.best_estimator_

                preds = cross_val_predict(model_GS.best_estimator_, X, y, cv=kf, n_jobs=-1,)
                
                gridsearches[model] = measures(preds, y)
                time2 = datetime.datetime.now()
                elapsedTime = time2 - time1
                elapsedTime
                datetime.timedelta(0, 125, 749430)
                difference = divmod(elapsedTime.total_seconds(), 60)
                timing = str("Time elapsed: {0} minutes ({1} seconds)".format(difference[0],difference[1]))
                m.trainings[str(modelname)+"@"+str(datetime.datetime.now())] = timing
                recordscount = str(len(X))
                if estimate != 1:
                    recordscount = str(round(len(X)*estimate))
                    estimate = 1
                else:
                    estimate = 0
                if m.stats:
                    import requests
                    data={'name': str(modelname),
                          'accuracy': str(gridsearches[model]['accuracy']),
                          'precision':str(gridsearches[model]['precision']),
                          'recall':str(gridsearches[model]['recall']),
                          'f1':str(gridsearches[model]['f1']),
                          'records_count': recordscount,
                          'attributes_count': str(X.shape[1]),
                          'hyperparameters': str(model),
                          'training_time':str(difference[0]*60.0+difference[1]),
                          'estimated':estimate
                          }
                    res = requests.post('https://mustafasa.com/op/trainings.php', data)
            except Exception as e:
                print(str(e)+" algorithm skipped")
            m.latesttraining = gridsearches
            if m.stats:
                print("Thank you for opting in to share your results to improve {mustafa} :)")
            else:
                print("Feel free to share your training results to improve {mustafa} by setting (stats=True) in the constructor :)")
        return gridsearches
    def best(m,rs=[]):
        mustafa(m,rs)
    def mustafa(m,rs=[]):
        h = 0
        requestskips = rs
        highalgo = ""
        m.modelsorder = dict()
        allowedskips = ['accuracy','recall','f1','precision']
        skip = ['matrix']
        
        for element in allowedskips:
            if element not in requestskips and len(requestskips) > 0:
                skip.append(element)
        
        for k,v in enumerate(m.latesttraining):
            temp = 0
            for element in m.latesttraining[v]:
                if element not in skip:
                    temp = temp + m.latesttraining[v][element]
            if temp >= h:
                highalgo = v
                h = temp
            m.modelsorder[v] = temp
            #print(m.modelsorder[v])
        print(highalgo,m.latesttraining[highalgo],' is mustafa')
        return {str(highalgo):m.latesttraining[highalgo]}

    def successful(m):
        a = []
        for k in m.trainings:
            a.append(k.split('@')[0])
        return a
    def votingclassifiers(m):
        return m.votingalgos
    def results(m):
        dicy = m.latesttraining
        for k in dicy:
            print(k)
            for value in dicy[k]:
                print(value,":")
                print(dicy[k][value])
            print()
        return m.latesttraining
    
    def vote(m,X,y,n=-1,splits=2,customset=[]):
        if len(m.modelsorder) == 0 and len(customset) == 0:
            m.mustafa()
        gridsearches = dict()
        from sklearn.model_selection import GridSearchCV, StratifiedKFold
        from sklearn.model_selection import cross_val_score, cross_val_predict
        kf = StratifiedKFold(n_splits=splits)
        from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve, cohen_kappa_score, f1_score, recall_score, precision_score
        import datetime
        dict1 = m.modelsorder
        sorted_tuples = sorted(dict1.items(), key=lambda item: item[1],reverse=True)
        sorted_dict = {k: v for k, v in sorted_tuples}
        candidates1 = list(sorted_dict.keys())
        if n > 0:
            candidates1 = list(sorted_dict.keys())[:n]
        biglist = []
        for element in candidates1:
            biglist.append((str(element),element))
        if len(customset) > 0:
            biglist = customset
        def measures(predicted, y_test):
            print()
            metrics = dict()
            accuracy = accuracy_score(y_test, predicted)
            metrics["accuracy"] = accuracy
            print('Accuracy: %f' % accuracy)
            precision = precision_score(y_test, predicted)
            metrics["precision"] = precision
            print('Precision: %f' % precision)
            recall = recall_score(y_test, predicted)
            metrics["recall"] = recall
            print('Recall: %f' % recall)
            f1 = f1_score(y_test, predicted)
            metrics["f1"] = f1
            print('F1 score: %f' % f1)
            matrix = confusion_matrix(y_test, predicted)
            metrics["matrix"] = matrix
            print('Confusion Matrix')
            print(matrix)
            print()
            return metrics

        for k,v in enumerate(m.votingalgos):
            #print(v)
            #print(m.dictclasses[v.__name__])
#             try:
            import sklearn
            import importlib

            model = getattr(importlib.import_module(f"sklearn.{m.dictclasses[v.__name__]}"), v.__name__)

            etc = model(estimators=biglist)
            modelname = model.__name__
            print(etc)
            etc_search_param= m.votingalgos[v]
            #etc_search_param['estimators'] 
            #print(m.votingalgos[v],"here")
            model_GS = GridSearchCV(estimator=etc,
                                 param_grid = etc_search_param,
                                 scoring=["accuracy", "recall"],
                                 refit="accuracy",
                                 verbose= -1,
                                 cv=kf,
                                 n_jobs=-1)
            time1 = datetime.datetime.now()
            model_GS.fit(X, y)
            model = model_GS.best_estimator_

            preds = cross_val_predict(model_GS.best_estimator_, X, y, cv=kf, n_jobs=-1,)

            gridsearches[model] = measures(preds, y)
            time2 = datetime.datetime.now()
            elapsedTime = time2 - time1
            elapsedTime
            datetime.timedelta(0, 125, 749430)
            difference = divmod(elapsedTime.total_seconds(), 60)
            timing = str("Time elapsed: {0} minutes ({1} seconds)".format(difference[0],difference[1]))
            m.trainings[str(modelname)+"@"+str(datetime.datetime.now())] = timing

#             except Exception as e:
#                 print(str(e)+" (algorithm skipped)")
            m.latesttraining = gridsearches
        return gridsearches
