from lime.lime_text import LimeTextExplainer
from nlp_inference import LABELS
from flask import current_app

_explainer = LimeTextExplainer(class_names=LABELS, random_state=42)

def lime_explain(classifier, text: str, num_features: int = 12, num_samples: int = 1000):
    # Allow passing None; fetch from Flask app store
    obj = classifier
    if obj is None:
        obj = getattr(current_app, "extensions", {}).get("clinical_classifier")

    # Accept either a callable or an object with predict_proba(_fn)
    predict_fn = None
    if callable(obj):
        predict_fn = obj
    elif obj is not None:
        predict_fn = getattr(obj, "predict_proba_fn", None) or getattr(obj, "predict_proba", None)

    print("predict_fn==", predict_fn)
    if predict_fn is None:
        raise ValueError("Classifier must be provided or registered and expose predict_proba(_fn)")

    # LIME sometimes passes numpy arrays; force list for tokenizer
    def _wrapped(batch):
        return predict_fn(list(batch))

    exp = _explainer.explain_instance(
        text_instance=text,
        classifier_fn=_wrapped,
        num_features=num_features,
        num_samples=num_samples
    )
    print("exp==", exp)
    return exp.as_html()
