#!/bin/bash

LAYER_NAME="ocr-pdf"
BUCKET_NAME="dv-product-bucket"
S3_PATH="layers/ocr-pdf-layer.zip"
PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")

LAYER_DIR="$PROJECT_ROOT/$LAYER_NAME"
mkdir -p $LAYER_DIR
pip install -r $PROJECT_ROOT/requirements.pdf.txt -t $LAYER_DIR/python
cd $PROJECT_ROOT/$LAYER_NAME
zip -r ocr-pdf-layer.zip .

aws s3 cp ocr-pdf-layer.zip s3://$BUCKET_NAME/$S3_PATH

aws lambda publish-layer-version \
  --layer-name $LAYER_NAME \
  --description "Dependencies for OCR and PDF processing" \
  --content S3Bucket=$BUCKET_NAME,S3Key=$S3_PATH

rm -rf $PROJECT_ROOT/$LAYER_NAME
cd $PROJECT_ROOT
