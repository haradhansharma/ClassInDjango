class LabelWiseData:
        
    def __init__(self, evaluator):
        # The evaluator can be either from session or url which will be supplied
        self.evaluator = evaluator   
        # We will neeed total active questions in the site to use by filtering sing diferent parameter     
        self.active_questions = Question.objects.filter(is_active=True)
        # we will need the statment added from the selected options during answering for this report/evaluator, must be excluded assesments or logical strings
        self.eva_label_statement = EvaLebelStatement.objects.filter(evaluator = self.evaluator, question__isnull = False, assesment = False)  
        
        
    def total_active_questions(self):
        data = self.active_questions.count()
        return round(data, 2)
    
    def total_positive_answer(self):
        data = self.eva_label_statement.filter(positive = 1).values('question').distinct().count()
        return round(data, 2)
    
    def total_nagetive_answer(self):
        data = self.eva_label_statement.filter(positive = 0).values('question').distinct().count()
        return round(data, 2)
    
    def overview_green(self):
        data = (self.total_positive_answer()/self.total_active_questions())*100
        return round(data, 2)
    
    def overview_red(self):
        data = (self.total_nagetive_answer()/self.total_active_questions())*100
        return round(data, 2)
    
    def overview_grey(self):
        '''
        As overview green and overview red is in parcent so we will deduct from 100 the both to equalized dividation in barchart.
        As each question have no label and have multiple positive value or negative value so sum of labelwise questions result is diferent then actual total question.
        For this reason to get rid of the mismatched result we had to deduct from 100 to get matching report in the barchart.        
        '''
        data = 100 - (self.overview_green() + self.overview_red())    
        return round(data, 2)
    
    def total_result(self):
        '''
        As per writen CSS our fist stacked bar will be green, second bar will be grey and third bar will be red so 
        we will placed the value in the list acordingly. We need to decide label name here so that it will be easy to impleted along with labels as each label has predifiened name.
        '''
        record = {
            #green>>grey>>red
            'Overview' : [self.overview_green(), self.overview_grey(), self.overview_red()]
            }
        return record
    
    def label_wise_positive_answered(self, label):  
        evalebel = label.labels.all()         
        data = self.eva_label_statement.filter(evalebel__in = evalebel, positive = 1).count()
        return round(data, 2)
    
    def label_wise_nagetive_answered(self, label): 
        evalebel = label.labels.all()    
        data = self.eva_label_statement.filter(evalebel__in = evalebel, positive = 0).count()
        return round(data, 2)
    
    def label_wise_result(self):       
        labels = DifinedLabel.objects.filter(common_status = False)
        record_dict = {}
        for label in labels:             
            positive = round(self.active_questions.filter(questions__name = label, questions__value = 1).count(), 2)  
            positive_answered = self.label_wise_positive_answered(label)        
            negative = round(self.active_questions.filter(questions__name = label, questions__value = 0).count(), 2)
            negative_answered = self.label_wise_nagetive_answered(label)    
            green = round((positive_answered/positive)*100, 2)
            red = round((negative_answered/negative)*100, 2)        
            record = {
                #Same as total total result
                #green>>grey>>red
                label.name : [green , round(100-(green+red),2), red]
            }        
            record_dict.update(record)         
        return record_dict
    
    def picked_labels_dict(self):
        label_result = {}    
        label_result.update(self.label_wise_result())
        label_result.update(self.total_result()) 
        return label_result
    
    def packed_labels(self):
        
        '''
        From dataframe we will take rows to use in JS's series.
        '''
        df = pd.DataFrame(self.picked_labels_dict())   
        return df
    
    def label_data_history(self):
        data = LabelDataHistory.objects.filter(evaluator = self.evaluator) 
        result_dict=[]
        for d in data:
            item_dict = {
                (d.created).strftime('%d-%m-%Y') : eval(d.items)
                }
            result_dict.append(item_dict)
        date_wise_df_list = []
        for rd in result_dict:
            for key, values in rd.items():
                vf = pd.DataFrame(values)
                vf_label = vf.columns.values.tolist()
                vf_data = vf.values.tolist()
                date_wise_df = {
                    key : [vf_label, vf_data]
                }
                date_wise_df_list.append(date_wise_df)
        
        return date_wise_df_list
