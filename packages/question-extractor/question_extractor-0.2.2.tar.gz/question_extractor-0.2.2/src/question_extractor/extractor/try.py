import train_predict_extract_question
model_name = "nltk_question_statement_df_model_RBF_SVM_6-17-0"
model_filepath = f"models/{model_name}.sav"
model = train_predict_extract_question.classification_model(mode="predict")
model.predict_init(model_filepath)
sentence = "many ppl do this but, what is your name?"
sentence = train_predict_extract_question.extract_question(str(sentence), model, only_direct=True)

print(sentence)
