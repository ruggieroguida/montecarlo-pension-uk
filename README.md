# Montecarlo simulation for UK retirement

**Disclaimer**: No financial advice is given or implied. Author is not a registered investment advisor. Information provided for educational purposes only.

An attempt to develop a simple calculator to estimate the probability of a comfortable retirement. **There are several assumptions that need to be verified.**

Feel free to open an issue with suggestions. I am not a financial expert or advisor.

## Install
You need a working Python 3 installation. Open a terminal in your preferred location then

```
git clone https://github.com/ruggieroguida/montecarlo-pension-uk.git
cd montecarlo-pension-uk/
pip3 install virtualenv
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
```

## Use

- Copy `inputs_sample.json` to `inputs.json`
- Edit `inputs.json` with your data
- Run `python3 montecarlo.py`

 
