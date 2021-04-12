let scoreThreshold = 0.7
let sizeType = '160'
let modelLoaded = false
var cImg;
var constraints = {
         audio: false,
          video: {
          width: 500,
           height: 300
}
};
var EmotionModel;
var offset_x = 27;
var offset_y = 20;
var emotion_labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"];
var emotion_colors = ["#ff0000", "#00a800", "#ff4fc1", "#ffe100", "#306eff", "#ff9d00", "#7c7c7c"];


async function onPlay(videoEl) {
    if (videoEl.paused || videoEl.ended || !modelLoaded)
                return false

    const {
                width,
                height
            } = faceapi.getMediaDimensions(videoEl)
            const canvas = $('#overlay').get(0)
            canvas.width = width
            canvas.height = height

            const forwardParams = {
                inputSize: parseInt(sizeType),
                scoreThreshold
            }

            const ts = Date.now()
            const result = await faceapi.detectAllFaces(videoEl, new faceapi.TinyFaceDetectorOptions(forwardParams))
            console.result
            if (result.length != 0) {
                const context = canvas.getContext('2d')
                context.drawImage(videoEl, 0, 0, width, height)
                let ctx = context;
                ctx.lineWidth = 4;
                ctx.font = "25px Arial"
                ctx.fillText('Result', 0, 0);

                for (var i = 0; i < result.length; i++) {
                    ctx.beginPath();
                    var item = result[i].box;
                    let s_x = Math.floor(item._x+offset_x);
                    if (item.y<offset_y){
                        var s_y = Math.floor(item._y);
                    }
                    else{
                        var s_y = Math.floor(item._y-offset_y);
                    }
                    let s_w = Math.floor(item._width-offset_x);
                    let s_h = Math.floor(item._height);
                    let cT = ctx.getImageData(s_x, s_y, s_w, s_h);
                    cT = preprocess(cT);

                    z = await EmotionModel.predict(cT);
                    let index = z.argMax(1).dataSync()[0]
                    let label = emotion_labels[index];
                    document.getElementById('mood').value = index;
                    ctx.strokeStyle = emotion_colors[index];
                    ctx.rect(s_x, s_y, s_w, s_h);
                    ctx.stroke();
                    ctx.fillStyle = emotion_colors[index];
                    ctx.fillText(label, s_x, s_y);
                    ctx.closePath();
                }
            }
            setTimeout((){ onPlay(videoEl)},100;)
            var status = document.getElementById('status');
            status.innerHTML = "Running the model ... ";
        }
        async function loadNetWeights(uri) {
            return new Float32Array(await (await fetch(uri)).arrayBuffer())
        }
        // create model
        async function createModel(path) {
            let model = await tf.loadLayersModel(path)
            return model
        }
        // load emotion model
        async function loadModel(path) {
            EmotionModel = await createModel(path)
            console.log('EMotion Model Loaded');
        }

        function preprocess(imgData) {
            return tf.tidy(() => {
                let tensor = tf.browser.fromPixels(imgData).toFloat();

                tensor = tensor.resizeBilinear([100, 100])

                tensor = tf.cast(tensor, 'float32')
                const offset = tf.scalar(255.0);
                // Normalize the image 
                const normalized = tensor.div(offset);
                //We add a dimension to get a batch shape 
                const batched = normalized.expandDims(0)
                return batched
            })
        }

        function successCallback(stream) {
            var videoEl = $('#inputVideo').get(0)
            videoEl.srcObject = stream;
        }

        function errorCallback(error) {
            alert(error)
            console.log("navigator.getUserMedia error: ", error);
        }

        async function run() {
            const Model_url = '../static/models/tiny_face_detector/tiny_face_detector_model-weights_manifest.json'
            await faceapi.loadTinyFaceDetectorModel(Model_url)
            modelLoaded = true
                 
            console.log("fetector Loaded");
            var status = document.getElementById('status');
            status.innerHTML = "Initializing the camera ... ";

            navigator.mediaDevices.getUserMedia(constraints)
                .then(successCallback)
                .catch(errorCallback);

            onPlay($('#inputVideo').get(0))
        
        }

         $(document).ready(async function(){
            EmotionModel = await tf.loadLayersModel('../static/models/mobilenetv1_models/model.json');
            const sizeTypeSelect = $('#sizeType');
            sizeTypeSelect.val(sizeType);
            run();
        }());
