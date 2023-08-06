from sentence_splitter import SentenceSplitter, split_text_into_sentences
from tqdm.auto import tqdm
from api import AutoReWrite

if __name__ == "__main__":
    text = """
    
    The Border Collie is a British breed of herding dog of medium size. They are descended from landrace sheepdogs once found all over the British Isles, but became standardized in the Anglo-Scottish border region. Presently they are used primarily as working dogs to herd livestock, specifically sheep.[1]
    
    The Border Collie is considered a highly intelligent, extremely energetic, acrobatic and athletic dog. They frequently compete with great success in sheepdog trials and a range of dog sports like dog obedience, disc dog, herding and dog agility. They are one of the most intelligent domestic dog breeds.[2] Border Collies continue to be employed in their traditional work of herding livestock throughout the world and are kept as pets.
    
    
    """
    rewriter = AutoReWrite(api='http://192.168.1.18:3008')
    out = rewriter.rewriter(text, simlimit=0.7)
    print("".join(out))
