![logo](./pdfinvert/static/logo.png)

# invert-pdf.club
A free online PDF colour inverter. (Perfect for printing dark PDFs.)

Try it online at [invert-pdf.club](https://invert-pdf.club)!

## Running locally
### Docker (recommended)
```bash
sudo docker image build . -t invert-pdf
sudo docker run -p 8080:8080 --env PORT=8080 invert-pdf:latest
```
Open [localhost:8080](http://localhost:8080) and enjoy!

### Manually from source
1. Install ImageMagick and ghostscript from your package manager.
```bash
sudo apt install ImageMagick ghostscript
```
2. (Recommended) Use a virtual environment for your python dependencies.
```bash
virtualenv venv
source venv/bin/activate
```
3. Install python dependencies. (Python 3.6+)
```bash
pip install -r requirements.txt
```
4. (Optional) Run the tests.
```bash
sh run_tests.sh
```
5. Run the application in development mode.
```bash
python pdfinvert/main.py
```
