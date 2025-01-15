#!/bin/bash

LAYER_NAME="ocr-pdf"
BUCKET_NAME="dv-product-bucket"
S3_PATH="layers/ocr-pdf-layer.zip"
PYTHON_VERSION="python3.10"
PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")

LAYER_DIR="$PROJECT_ROOT/$LAYER_NAME/python/lib/$PYTHON_VERSION/site-packages"
mkdir -p $LAYER_DIR
pip install -r $PROJECT_ROOT/requirements.pdf.txt \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.10 \
  --only-binary=:all: \
  --upgrade \
  -t $LAYER_DIR
cd $PROJECT_ROOT/$LAYER_NAME
zip -r ocr-pdf-layer.zip .

aws s3 cp ocr-pdf-layer.zip s3://$BUCKET_NAME/$S3_PATH

aws lambda publish-layer-version \
  --layer-name $LAYER_NAME \
  --description "Dependencies for OCR and PDF processing" \
  --content S3Bucket=$BUCKET_NAME,S3Key=$S3_PATH \
  --compatible-runtimes $PYTHON_VERSION \
  --compatible-architectures x86_64

rm -rf $PROJECT_ROOT/$LAYER_NAME
cd $PROJECT_ROOT
