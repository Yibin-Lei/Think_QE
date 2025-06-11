conda create -n thinkqe_310 python=3.10
conda activate thinkqe_310
pip install -r requirements.txt
conda install -c conda-forge faiss-gpu openjdk=11 maven
python -m spacy download en_core_web_sm