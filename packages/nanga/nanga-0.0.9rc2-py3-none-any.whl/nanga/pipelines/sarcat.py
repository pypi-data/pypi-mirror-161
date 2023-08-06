from nanga.sarcat.models.legacy import load_model




class SarcatPipeline():
    """
    Sarcat pipeline
    """


    def __init__(self, model_name,
                 train=False,
                 predict=False):
        self.processor = 'predict' if predict else 'train'
        self.model, _ = load_model(model_name)


    def __call__(self,
                 title:str,
                 abstract:str,
                 return_mcats=True):
        if self.processor == 'predict':
            return self.model.predict(title, abstract, return_mcats)

