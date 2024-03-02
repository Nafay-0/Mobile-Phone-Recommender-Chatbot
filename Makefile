install:
		pip install --upgrade pip &&\
		pip install -r requirements.txt


start:
	    uvicorn src.app.main:app --reload
