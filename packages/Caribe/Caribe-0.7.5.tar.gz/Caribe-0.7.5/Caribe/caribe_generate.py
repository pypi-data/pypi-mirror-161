#Author: Keston Smith

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("model/", local_files_only=True)

class generate_text:
    def __init__(self, input, min_length:int= 10, max_length:int= 50, do_sample:bool = False, early_stopping:bool= False, num_beams:int= 4,temperature:float= 0.7, top_k: int = 50, no_repeat_ngram_size:int= 0, top_p: float = 1,  repetition_penalty:float=1.0):
        self.min_length=min_length
        self.max_length=max_length
        self.do_sample=do_sample
        self.early_stopping=early_stopping
        self.num_beams=num_beams
        self.temperature=temperature
        self.top_k=top_k
        self.no_repeat_ngram_size=no_repeat_ngram_size
        self.top_p=top_p
        self.repetition_penalty= repetition_penalty 
        self.input=input

    
    def output(self):    
        self.input_ids = tokenizer(self.input, return_tensors="pt").input_ids
        outputs = model.generate(self.input_ids, min_length=self.min_length, max_length=self.max_length, do_sample=self.do_sample, early_stopping=self.early_stopping, num_beams=self.num_beams, temperature=self.temperature,  top_k=self.top_k, no_repeat_ngram_size=self.no_repeat_ngram_size, top_p=self.top_p,  repetition_penalty=self.repetition_penalty)
        output_text= tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return "".join(output_text)  
        
