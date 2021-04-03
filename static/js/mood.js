function setText( text ,id) {
            document.getElementById(id).innerText = text;
        }

 function drawLine( ctx, x1, y1, x2, y2 ) {
            ctx.beginPath();
            ctx.moveTo( x1, y1 );
            ctx.lineTo( x2, y2 );
            ctx.stroke();
}

async function setupWebcam() {
            return new Promise( ( resolve, reject ) => {
                const webcamElement = document.getElementById( "webcam" );
                webcamElement.style.display = "none";
                const navigatorAny = navigator;
                navigator.getUserMedia = navigator.getUserMedia ||
                navigatorAny.webkitGetUserMedia || navigatorAny.mozGetUserMedia ||
                navigatorAny.msGetUserMedia;
                if( navigator.getUserMedia ) {
                    navigator.getUserMedia( { video: true },
                        stream => {
                            webcamElement.srcObject = stream;
                            webcamElement.addEventListener( "loadeddata", resolve, false );
                        },
                    error => reject());
                }
                else {
                    reject();
                }
            });
}

        const emotions = [ "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise" ];
        let emotionModel = null;
        let count =0;
        let currentEmotion = "neutral";
        let output = null;
        let model = null;

        async function predictEmotion( points ) {
            let result = tf.tidy( () => {
                const xs = tf.stack( [ tf.tensor1d( points ) ] );
                return emotionModel.predict( xs );
            });
            let prediction = await result.data();
            result.dispose();
            // Get the index of the maximum value
            let id = prediction.indexOf( Math.max( ...prediction ));
            return id;
        }

        async function trackFace() {
            const video = document.querySelector( "video" );
            const faces = await model.estimateFaces( {
                input: video,
                returnTensors: false,
                flipHorizontal: false,
            });
            output.drawImage(
                video,
                0, 0, video.width, video.height,
                0, 0, video.width, video.height
            );

            let points = null;
            faces.forEach( face => {
                // Draw the bounding box
                const x1 = face.boundingBox.topLeft[ 0 ];
                const y1 = face.boundingBox.topLeft[ 1 ];
                const x2 = face.boundingBox.bottomRight[ 0 ];
                const y2 = face.boundingBox.bottomRight[ 1 ];
                const bWidth = x2 - x1;
                const bHeight = y2 - y1;
                drawLine( output, x1, y1, x2, y1 );
                drawLine( output, x2, y1, x2, y2 );
                drawLine( output, x1, y2, x2, y2 );
                drawLine( output, x1, y1, x1, y2 );

                // Add just the nose, cheeks, eyes, eyebrows & mouth
                const features = [
                    "noseTip",
                    "leftCheek",
                    "rightCheek",
                    "leftEyeLower1", "leftEyeUpper1",
                    "rightEyeLower1", "rightEyeUpper1",
                    "leftEyebrowLower", //"leftEyebrowUpper",
                    "rightEyebrowLower", //"rightEyebrowUpper",
                    "lipsLowerInner", //"lipsLowerOuter",
                    "lipsUpperInner", //"lipsUpperOuter",
                ];
                points = [];
                features.forEach( feature => {
                    face.annotations[ feature ].forEach( x => {
                        points.push( ( x[ 0 ] - x1 ) / bWidth );
                        points.push( ( x[ 1 ] - y1 ) / bHeight );
                    });
                });
            });

            if( points ) {
                let emotion = await predictEmotion( points );
                document.getElementById("mood").value = emotion;
            }
            else {
                setText( "No Face" ,"status");
            }

            requestAnimationFrame( trackFace );
        }

        (async () => {
            await setupWebcam();
            const video = document.getElementById( "webcam" );
            video.play();
            let videoWidth = video.videoWidth;
            let videoHeight = video.videoHeight;
            video.width = videoWidth;
            video.height = videoHeight;

            let canvas = document.getElementById( "output" );
            canvas.width = video.width;
            canvas.height = video.height;

            output = canvas.getContext( "2d" );
            output.translate( canvas.width, 0 );
            output.scale( -1, 1 ); // Mirror cam
            output.fillStyle = "#fdffb6";
            output.strokeStyle = "#fdffb6";
            output.lineWidth = 2;

            // Load Face Landmarks Detection
            model = await faceLandmarksDetection.load(
                faceLandmarksDetection.SupportedPackages.mediapipeFacemesh
            );
            // Load Emotion Detection
            const MODEL_URL = '../static/models/facemo.json';
            emotionModel = await tf.loadLayersModel(MODEL_URL);

            setText( "Loaded!" ,"status");

            trackFace();
        })();