
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, avatar;

function init() {
    // Get the container where the 3D canvas should be added
    const container = document.querySelector('.main-content');

    // Scene
    scene = new THREE.Scene();
    scene.background = null;
    // scene.background = new THREE.Color(0x87ceeb); // Light blue background



    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 5, 0); // A better Z to actually view the model from front->(0,5,5)

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true ,alpha:true});
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
    directionalLight.position.set(1, 5, -1).normalize();
    scene.add(directionalLight);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1, 0);
    controls.update();

    // Load Model
    const loader = new GLTFLoader();
    loader.load(
        '/static/models/a4.glb',
        function (gltf) {
            avatar = gltf.scene;
            avatar.scale.set(1, 1, 1);
            avatar.position.set(0, 0, 0);
            scene.add(avatar);
            document.getElementById('info').textContent = 'Avatar Loaded!';
        },
        function (xhr) {
            const progress = (xhr.loaded / xhr.total) * 100;
            document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
        },
        function (error) {
            console.error('Error loading model:', error);
            document.getElementById('info').textContent = 'Error loading avatar!';
        }
    );

    // Resize handling
    window.addEventListener('resize', () => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    // Update controls if damping is enabled
    if (avatar) {
         // You can add animation updates here if your GLTF has animations
         // mixer.update(delta);
    }
    renderer.render(scene, camera);
}
init();
animate();

// import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// // let scene, camera, renderer, avatar;

// function init() {
//     // Scene
//     scene = new THREE.Scene();
//     scene.background = new THREE.Color(0x87ceeb); // Light blue background

//     // Camera
//     camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
//     camera.position.set(0, 5, 0); // Position camera to look at a typical avatar height

//     // Renderer
//     renderer = new THREE.WebGLRenderer({ antialias: true });
//     renderer.setSize(window.innerWidth, window.innerHeight);
//     document.body.appendChild(renderer.domElement);
//     // Lights
//     // const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
//     // scene.add(ambientLight);

//     const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
//     directionalLight.position.set(1, 5, -1).normalize();
//     scene.add(directionalLight);

//     // OrbitControls (for interaction)
//     const controls = new OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true; // smooth rotation
//     controls.dampingFactor = 0.05;
//     controls.target.set(0, 1, 0); // Target the center of the avatar typically

//     // Load GLTF Model
//     const loader = new GLTFLoader();
//     // The URL for the model is relative to the static folder, and Flask serves it
//     loader.load(
//         '/static/models/a4.glb', // **IMPORTANT: Replace with your actual model path**
//         function (gltf) {
//             avatar = gltf.scene;
//             // Scale or position your avatar as needed
//             avatar.scale.set(1, 1, 1);
//             avatar.position.set(0, 0, 0);
//             scene.add(avatar);
//             document.getElementById('info').textContent = 'Avatar Loaded!';
//         },
//         function (xhr) {
//             // Progress callback
//             const progress = (xhr.loaded / xhr.total * 100);
//             document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
//             console.log('Loading ' + progress + '% of model');
//         },
//         function (error) {
//             // Error callback
//             console.error('An error occurred while loading the model:', error);
//             document.getElementById('info').textContent = 'Error loading avatar!';
//         }
//     );

//     // Handle window resize
//     window.addEventListener('resize', onWindowResize, false);
// }

// function onWindowResize() {
//     camera.aspect = window.innerWidth / window.innerHeight;
//     camera.updateProjectionMatrix();
//     renderer.setSize(window.innerWidth, window.innerHeight);
// }

// function animate() {
//     requestAnimationFrame(animate);
//     // Update controls if damping is enabled
//     if (avatar) {
//          // You can add animation updates here if your GLTF has animations
//          // mixer.update(delta);
//     }
//     renderer.render(scene, camera);
// }
// init();
// animate();


/*
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, avatar;
let audio, audioLoader;
let lipSyncData = [];
let currentPhonemeIndex = 0;
let avatarMeshesWithMorphTargets = []; // To store meshes that have morph targets

// Define your string here
const SPEECH_TEXT = "Hello, world! This is a lip-sync demo.";
const AUDIO_FILE_PATH = '/static/audio/hello_world.mp3'; // Path to your generated audio
const LIPSINC_DATA_PATH = '/static/data/lipsync_data.json'; // Path to your generated phoneme data

// Map of common viseme names to their blend shape indices (will be populated dynamically)
const visemeMorphTargetIndices = {};

function init() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb); // Light blue background

    // Camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.5, 3); // Position camera to look at a typical avatar height

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth / 2, window.innerHeight / 2); // Reduced size for demo
    document.body.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 2, 4).normalize();
    scene.add(directionalLight);

    // OrbitControls (for interaction)
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // smooth rotation
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1, 0); // Target the center of the avatar typically

    // Audio setup
    const listener = new THREE.AudioListener();
    camera.add(listener);
    audio = new THREE.Audio(listener);
    audioLoader = new THREE.AudioLoader();

    // UI for starting playback
    const startButton = document.createElement('button');
    startButton.textContent = 'Start Lip-Sync (Play Audio)';
    startButton.style.position = 'absolute';
    startButton.style.bottom = '20px';
    startButton.style.left = '50%';
    startButton.style.transform = 'translateX(-50%)';
    startButton.style.padding = '10px 20px';
    startButton.style.fontSize = '18px';
    startButton.style.cursor = 'pointer';
    document.body.appendChild(startButton);

    startButton.addEventListener('click', () => {
        if (audio && lipSyncData.length > 0) {
            audio.play();
            currentPhonemeIndex = 0; // Reset for new playback
            document.getElementById('info').textContent = 'Playing audio...';
        } else {
            document.getElementById('info').textContent = 'Audio or lip-sync data not ready.';
        }
    });

    // Load GLTF Model
    const loader = new GLTFLoader();
    loader.load(
        '/static/models/a4.glb', // **IMPORTANT: Replace with your actual model path**
        function (gltf) {
            avatar = gltf.scene;
            avatar.scale.set(1, 1, 1);
            avatar.position.set(0, 0, 0);
            scene.add(avatar);
            document.getElementById('info').textContent = 'Avatar Loaded!';

            // Collect all meshes that have morph targets
            avatar.traverse((o) => {
                if (o.isMesh && o.morphTargetDictionary && o.morphTargetInfluences) {
                    avatarMeshesWithMorphTargets.push(o);
                    // Store the index for each possible viseme blend shape
                    for (const visemeName in o.morphTargetDictionary) {
                        visemeMorphTargetIndices[visemeName] = o.morphTargetDictionary[visemeName];
                    }
                    console.log("Found blend shapes:", Object.keys(o.morphTargetDictionary));
                }
            });

            if (avatarMeshesWithMorphTargets.length === 0) {
                console.warn('No meshes with morph targets found on the avatar. Lip-sync will not work.');
                document.getElementById('info').textContent = 'Error: No blend shapes found on avatar!';
            } else {
                loadAudioAndLipSyncData();
            }
        },
        function (xhr) {
            const progress = (xhr.loaded / xhr.total * 100);
            document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
            console.log('Loading ' + progress + '% of model');
        },
        function (error) {
            console.error('An error occurred while loading the model:', error);
            document.getElementById('info').textContent = 'Error loading avatar!';
        }
    );

    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
}

function loadAudioAndLipSyncData() {
    // Load audio
    audioLoader.load(AUDIO_FILE_PATH, function (buffer) {
        audio.setBuffer(buffer);
        document.getElementById('info').textContent = 'Audio loaded. Loading lip-sync data...';
    }, undefined, function (err) {
        console.error('Error loading audio:', err);
        document.getElementById('info').textContent = 'Error loading audio!';
    });

    // Load lip-sync data (JSON)
    fetch(LIPSINC_DATA_PATH)
        .then(response => response.json())
        .then(data => {
            lipSyncData = data.sort((a, b) => a.time - b.time); // Ensure data is sorted by time
            document.getElementById('info').textContent = 'Lip-sync data loaded. Click "Start Lip-Sync"';
            console.log('Lip-sync data:', lipSyncData);
        })
        .catch(error => {
            console.error('Error loading lip-sync data:', error);
            document.getElementById('info').textContent = 'Error loading lip-sync data!';
        });
}

// Function to set all blend shapes to 0 influence
function resetAllVisemes() {
    avatarMeshesWithMorphTargets.forEach(mesh => {
        if (mesh.morphTargetInfluences) {
            for (let i = 0; i < mesh.morphTargetInfluences.length; i++) {
                mesh.morphTargetInfluences[i] = 0;
            }
        }
    });
}

function applyViseme(visemeName, influence = 1.0) {
    // Reset all visemes first to avoid overlapping shapes (optional, but often good)
    resetAllVisemes();

    avatarMeshesWithMorphTargets.forEach(mesh => {
        const visemeIndex = visemeMorphTargetIndices[visemeName];
        if (visemeIndex !== undefined && mesh.morphTargetInfluences) {
            mesh.morphTargetInfluences[visemeIndex] = influence;
        }
    });
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth / 2, window.innerHeight / 2); // Keep reduced size
}

function animate() {
    requestAnimationFrame(animate);

    if (audio && audio.isPlaying && lipSyncData.length > 0 && avatarMeshesWithMorphTargets.length > 0) {
        const currentTime = audio.context.currentTime - audio.startTime;

        // Advance through phonemes based on current audio time
        while (currentPhonemeIndex < lipSyncData.length - 1 &&
               lipSyncData[currentPhonemeIndex + 1].time <= currentTime) {
            currentPhonemeIndex++;
        }

        const currentPhoneme = lipSyncData[currentPhonemeIndex];
        // console.log(`Time: ${currentTime.toFixed(2)}, Viseme: ${currentPhoneme.viseme}`);

        // Apply the current viseme. You might want to add interpolation here
        // to smooth transitions between visemes, especially for short phonemes.
        applyViseme(currentPhoneme.viseme, 1.0); // Apply full influence for now

        // Optionally, reset to idle when audio finishes
        if (!audio.isPlaying && currentTime >= audio.buffer.duration) {
            applyViseme('viseme_idle', 1.0); // Or whatever your idle/closed mouth blend shape is
            currentPhonemeIndex = 0; // Reset for next play
        }
    } else if (avatar && avatarMeshesWithMorphTargets.length > 0 && !audio.isPlaying) {
        // Ensure mouth is closed/idle when not speaking
        applyViseme('viseme_idle', 1.0); // Ensure your model has a 'viseme_idle' or similar
    }


    renderer.render(scene, camera);
}

init();
animate();
*/