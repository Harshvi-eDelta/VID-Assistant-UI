// import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// let scene, camera, renderer, avatar;
// // let audio, audioLoader;
// // let lipSyncData = [];
// // let currentPhonemeIndex = 0;
// // let avatarMeshesWithMorphTargets = []; // To store meshes that have morph targets

// // // Define your string here
// // const SPEECH_TEXT = "in being comparatively modern";
// // const AUDIO_FILE_PATH = '/static/audio/2.wav'; // Path to your generated audio
// // const LIPSINC_DATA_PATH = '/static/data/lipsync_data.json'; // Path to your generated phoneme data

// function init() {
//     const container = document.querySelector('.main-content');

//     // Scene
//     scene = new THREE.Scene();
//     scene.background = null; // Light blue background

//     // Camera
//     camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
//     camera.position.set(0, 5, 0); // Position camera to look at a typical avatar height

//     // Renderer
//     renderer = new THREE.WebGLRenderer({ antialias: true ,alpha:true});
//     renderer.setSize(container.clientWidth, container.clientHeight); // Reduced size for demo
//     container.appendChild(renderer.domElement);

//     // Lights
//     const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
//     scene.add(ambientLight);

//     const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
//     directionalLight.position.set(1, 5, 2).normalize();
//     scene.add(directionalLight);

//     // OrbitControls (for interaction)
//     const controls = new OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true; // smooth rotation
//     controls.dampingFactor = 0.05;
//     controls.target.set(0, 1, 0); // Target the center of the avatar typically
//     controls.update();

//     // // Audio setup
//     // const listener = new THREE.AudioListener();
//     // camera.add(listener);
//     // audio = new THREE.Audio(listener);
//     // audioLoader = new THREE.AudioLoader();

//     // const micButton = document.getElementById('micButton');

//     // micButton.addEventListener('click', () => {
//     //     console.log("click mic.....")
//     //     if (audio) {
//     //         console.log("play audio....",audio)
//     //         audio.play();
//     //         currentPhonemeIndex = 0; // Reset for new playback
//     //         document.getElementById('info').textContent = 'Playing audio...';
//     //     } else {
//     //         console.log("no audio or data")
//     //         document.getElementById('info').textContent = 'Audio or lip-sync data not ready.';
//     //     }
//     // });

//     // Load GLTF Model
//     const loader = new GLTFLoader();
//     loader.load(
//         '/static/models/a4.glb', // **IMPORTANT: Replace with your actual model path**
//         function (gltf) {
//             avatar = gltf.scene;
//             avatar.scale.set(1, 1, 1);
//             avatar.position.set(0, 0, -1.5);
//             scene.add(avatar);
//             // document.getElementById('info').textContent = 'Avatar Loaded!';
//             console.log("avatar loaded!.....")
//             console.log(avatar)
//         },
//         function (xhr) {
//             const progress = (xhr.loaded / xhr.total * 100);
//             document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
//             console.log('Loading ' + progress + '% of model');
//         },
//         function (error) {
//             console.error('An error occurred while loading the model:', error);
//             document.getElementById('info').textContent = 'Error loading avatar!';
//         }
//     );

//     // Handle window resize
//     // window.addEventListener('resize', onWindowResize, false);
//     window.addEventListener('resize', () => {
//                 const width = container.clientWidth;
//                 const height = container.clientHeight;
//                 camera.aspect = width / height;
//                 camera.updateProjectionMatrix();
//                 renderer.setSize(width, height);
//             });
// }


// function animate() {
//     requestAnimationFrame(animate);
//     renderer.render(scene, camera);
// }

// init();
// animate(); 

// =======================================
// new code with dynamic updation

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, avatar;
let controls; 
// let audio, audioLoader;
// let lipSyncData = [];
// let currentPhonemeIndex = 0;
// let avatarMeshesWithMorphTargets = []; // To store meshes that have morph targets

function loadGLB(path) {
    if (avatar) {
        scene.remove(avatar);
    }

const clock = new THREE.Clock();

function init() {
    const container = document.querySelector('.main-content');

    // Scene
    scene = new THREE.Scene();
    scene.background = null; // Light blue background

    // Camera
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 5,0); // Position camera to look at a typical avatar height

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true ,alpha:true});
    renderer.setSize(container.clientWidth, container.clientHeight); // Reduced size for demo
    container.appendChild(renderer.domElement);

    // Lights
    // const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    // scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
    directionalLight.position.set(0, 5, 0).normalize();
    scene.add(directionalLight);

    // OrbitControls (for interaction)
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // smooth rotation
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1, 0); // Target the center of the avatar typically
    controls.update();
    

    // // Audio setup
    // const listener = new THREE.AudioListener();
    // camera.add(listener);
    // audio = new THREE.Audio(listener);
    // audioLoader = new THREE.AudioLoader();

    // const micButton = document.getElementById('micButton');

    // micButton.addEventListener('click', () => {
    //     console.log("click mic.....")
    //     if (audio) {
    //         console.log("play audio....",audio)
    //         audio.play();
    //         currentPhonemeIndex = 0; // Reset for new playback
    //         document.getElementById('info').textContent = 'Playing audio...';
    //     } else {
    //         console.log("no audio or data")
    //         document.getElementById('info').textContent = 'Audio or lip-sync data not ready.';
    //     }
    // });

    // Load GLTF Model
    const loader = new GLTFLoader();
    const cacheBustedPath = `${path}?t=${Date.now()}`;

    loader.load(
        cacheBustedPath,
        function (gltf) {
            avatar = gltf.scene;

            // 🚨 RESET ALL TRANSFORMS
            avatar.position.set(0, 0, -1.5);
            avatar.scale.set(1, 1, 1);
            avatar.rotation.set(0, 0, 0);

            // ✅ FIX: Rotate to face camera
            // This is the REAL fix
            console.log((Math.PI/2)*0.5)
            avatar.rotation.x = (Math.PI/2); // Lift it upright
            // avatar.rotation.y = Math.PI / 10;      // Face the front

            scene.add(avatar);
            document.getElementById('info').textContent = 'Avatar Loaded!';
        },
        function (xhr) {
            const progress = (xhr.loaded / xhr.total * 100);
            document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
        },
        function (error) {
            console.error('Error loading GLB:', error);
            document.getElementById('info').textContent = 'Error loading avatar!';
        }
    );
}


function init() {
    const container = document.querySelector('.main-content');

    scene = new THREE.Scene();
    scene.background = null;

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 5, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
    directionalLight.position.set(0, 5, 0).normalize();
    scene.add(directionalLight);

    // OrbitControls (for interaction)
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // smooth rotation
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1.6, 0); // Target the center of the avatar typically
    controls.update();

    // const controls = new OrbitControls(camera, renderer.domElement);
    // controls.enableDamping = true;
    // controls.dampingFactor = 0.05;
    // controls.target.set(0, 1, 0);
    // controls.update();

    window.addEventListener('resize', () => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });

    if (window.selectedAvatarName) {
        const glbPath = `/static/models/${window.selectedAvatarName}.glb`;
        loadGLB(glbPath);
    } else {
        console.warn("No selected avatar; skipping default.");
    }
}

// function animate() {
//     requestAnimationFrame(animate);
//     renderer.render(scene, camera);
// }

function animate() {

    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    // const delta = clock.getDelta();
    if (avatar) { // Ensure avatar is loaded
        // Rotate around the Y-axis. Adjust the `0.5` value to change rotation speed.
        // Higher value = faster rotation.
        // avatar.rotation.y += 0.5 * delta;
        // If you want X or Z rotation, you can add them similarly:
        // avatar.rotation.x += 0.1 * delta;
        // avatar.rotation.z += 0.1 * delta;
        const oscillationSpeed = 0.5; // Adjust this value to make it faster or slower
        const oscillationAmplitude = Math.PI/11; // Adjust this for a wider or narrower swing (in radians)
        avatar.rotation.z = Math.sin(elapsedTime * oscillationSpeed) * oscillationAmplitude;
    }
    controls.update();
    renderer.render(scene, camera);
    // requestAnimationFrame(animate);
}

function bindAvatarThumbnailClicks() {
    document.querySelectorAll('.avatar-thumbnail').forEach(img => {
        img.addEventListener('click', function () {
            const glbPath = this.getAttribute('data-glb');
            if (glbPath) {
                loadGLB(glbPath);
            }
        });
    });
}

// ✅ Utility: Wait for image to be fully available
function checkImageReady(url, attempts = 10) {
    return new Promise((resolve, reject) => {
        const tryLoad = (triesLeft) => {
            const testImg = new Image();
            testImg.onload = () => resolve(url + '?t=' + Date.now());
            testImg.onerror = () => {
                if (triesLeft <= 0) {
                    reject("Image still not ready.");
                } else {
                    setTimeout(() => tryLoad(triesLeft - 1), 500); // retry after 500ms
                }
            };
            testImg.src = url + '?t=' + Date.now();
        };
        tryLoad(attempts);
    });
}

// ✅ DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    init();
    animate();
    bindAvatarThumbnailClicks();

    const createBtn = document.querySelector('.create-btn');
    const fileInput = document.querySelector('#upload');
    const nameInput = document.querySelector('#avatarName');

    createBtn?.addEventListener('click', () => {
        const file = fileInput.files[0];
        const avatarName = nameInput.value.trim();

        if (!file || !avatarName) {
            alert("Please upload an image and enter a name.");
            return;
        }

        const formData = new FormData();
        formData.append('image', file);
        formData.append('avatar_name', avatarName);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                const glbPath = data.glb_url;
                const jpgPath = data.jpg_url;
                window.selectedAvatarName = data.avatar_name; // <-- Set this correctly
                // Load GLB immediately
                loadGLB(`${glbPath}?t=${Date.now()}`);
        
                const gallery = document.querySelector('.avatar-gallery');

                const card = document.createElement('div');
                card.className = 'avatar-card';

                const inner = document.createElement('div');

                const img = document.createElement('img');
                img.src = `/static/uploads/${data.avatar_name}.png?t=${Date.now()}`;
                img.alt = data.avatar_name;
                img.className = 'avatar-thumbnail';
                img.setAttribute('data-glb', `/static/models/${data.avatar_name}.glb`);
                img.onerror = function () {
                    this.src = '/static/images/default_avatar.jpg';
                };

                const label = document.createElement('p');
                label.textContent = data.avatar_name;

                inner.appendChild(img);
                inner.appendChild(label);
                card.appendChild(inner);
                gallery.insertBefore(card, gallery.firstChild);

                // Rebind thumbnail click
                img.addEventListener('click', function () {
                    const glbPath = this.getAttribute('data-glb');
                    loadGLB(glbPath);
                });
        
                alert("✅ Avatar created successfully!");
            } else {
                alert(`❌ Upload failed: ${data.message}`);
            }
        })
        .catch(err => {
            console.error("Upload error:", err);
            alert("Something went wrong during upload.");
        });        
    });
});

window.loadGLB = loadGLB;


// =======================================

// import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// let scene, camera, renderer, avatar;
// let audio, audioLoader;
// let audioLoaded = false; // Flag to track if audio is loaded
// // Removed: let lipSyncData = [];
// // Removed: let currentPhonemeIndex = 0;
// // Removed: let avatarMeshesWithMorphTargets = []; // To store meshes that have morph targets

// // // Define your string here (not used for audio playback only)
// const SPEECH_TEXT = "in being comparatively modern";
// const AUDIO_FILE_PATH = '/static/audio/2.wav'; // Path to your generated audio
// // Removed: const LIPSINC_DATA_PATH = '/static/data/lipsync_data.json'; // Path to your generated phoneme data

// // Removed: Map of common viseme names to their blend shape indices (will be populated dynamically)
// // Removed: const visemeMorphTargetIndices = {};

// function init() {
//     const container = document.querySelector('.main-content');

//     // Scene
//     scene = new THREE.Scene();
//     scene.background = null; // Light blue background

//     // Camera
//     camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
//     camera.position.set(0, 5, 0); // Position camera to look at a typical avatar height

//     // Renderer
//     renderer = new THREE.WebGLRenderer({ antialias: true ,alpha:true});
//     renderer.setSize(container.clientWidth, container.clientHeight); // Reduced size for demo
//     container.appendChild(renderer.domElement);

//     // Lights
//     const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
//     scene.add(ambientLight);

//     const directionalLight = new THREE.DirectionalLight(0xffffff, 10);
//     directionalLight.position.set(1, 5, 2).normalize();
//     scene.add(directionalLight);

//     // OrbitControls (for interaction)
//     const controls = new OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true; // smooth rotation
//     controls.dampingFactor = 0.05;
//     controls.target.set(0, 1, 0); // Target the center of the avatar typically
//     controls.update();

//     // Audio setup
//     const listener = new THREE.AudioListener();
//     camera.add(listener);
//     audio = new THREE.Audio(listener);
//     audioLoader = new THREE.AudioLoader();

//     // Removed: Lip-sync data loading
//     // fetch(LIPSINC_DATA_PATH)
//     //     .then(response => {
//     //         if (!response.ok) {
//     //             throw new Error(`HTTP error! status: ${response.status}`);
//     //         }
//     //         return response.json();
//     //     })
//     //     .then(data => {
//     //         lipSyncData = data;
//     //         document.getElementById('info').textContent = 'Lip-sync data loaded.';
//     //         console.log("Lip-sync data loaded successfully:", lipSyncData);
//     //     })
//     //     .catch(error => {
//     //         console.error('Error loading lip-sync data:', error);
//     //         document.getElementById('info').textContent = 'Error loading lip-sync data!';
//     //     });

//     function load_Audio(){
//         // IMPORTANT: Load the audio file here!
//         audioLoader.load(AUDIO_FILE_PATH, function(buffer) {
//             audio.setBuffer(buffer);
//             audio.setLoop(false); // Set to true if you want it to loop
//             audio.setVolume(0.5); // Adjust volume as needed
//             document.getElementById('info').textContent = 'Audio loaded. Click the mic button to play.';
//             console.log("Audio buffer loaded successfully.");
//         },
//         function (xhr) {
//             // Optional: Progress callback for audio loading
//             console.log((xhr.loaded / xhr.total * 100) + '% loaded audio');
//         },
//         function (err) {
//             console.error('An error occurred while loading the audio:', err);
//             document.getElementById('info').textContent = 'Error loading audio!';
//         });

//     }

//     const micButton = document.getElementById('micButton');
//     micButton.addEventListener('click', () => {
//         console.log("Mic button clicked.");

//         if (!audioLoaded) {
//             // Audio not loaded yet, initiate loading and then play
//             document.getElementById('info').textContent = 'Loading audio...';
//             console.log("Loading audio from:", AUDIO_FILE_PATH);

//             audioLoader.load(AUDIO_FILE_PATH, function(buffer) {
//                 audio.setBuffer(buffer);
//                 audio.setLoop(false);
//                 audio.setVolume(0.5);
//                 audioLoaded = true; // Set flag to true once loaded
//                 document.getElementById('info').textContent = 'Audio loaded and playing.';
//                 console.log("Audio buffer loaded successfully. Playing audio...");
//                 audio.play(); // Play immediately after loading
//             },
//             function (xhr) {
//                 // Optional: Progress callback for audio loading
//                 const progress = (xhr.loaded / xhr.total * 100);
//                 document.getElementById('info').textContent = `Loading audio: ${progress.toFixed(2)}%`;
//                 console.log(`Loading audio: ${progress.toFixed(2)}%`);
//             },
//             function (err) {
//                 console.error('An error occurred while loading the audio:', err);
//                 document.getElementById('info').textContent = 'Error loading audio!';
//             });
//         } else if (audio.buffer) {
//             // Audio already loaded
//             console.log("Audio already loaded.");

//             // *** NEW: Stop audio if it's currently playing ***
//             if (audio.isPlaying) {
//                 audio.stop();
//                 console.log("Audio stopped. Restarting...");
//             }

//             // Play it from the beginning
//             audio.play();
//             document.getElementById('info').textContent = 'Playing audio...';
//         } else {
//             document.getElementById('info').textContent = 'Audio is in an unexpected state. Try again.';
//             console.log("Audio in unexpected state.");
//         }
//     });

//     // Load GLTF Model
//     const loader = new GLTFLoader();
//     loader.load(
//         '/static/models/a4.glb', // **IMPORTANT: Replace with your actual model path**
//         function (gltf) {
//             avatar = gltf.scene;
//             avatar.scale.set(1, 1, 1);
//             avatar.position.set(0, 0, 0);
//             scene.add(avatar);
//             console.log("Avatar loaded!.....")
//             console.log(avatar)

//             // Removed: Populate avatarMeshesWithMorphTargets and visemeMorphTargetIndices after avatar is loaded
//             // avatar.traverse(node => {
//             //     if (node.isMesh && node.morphTargetInfluences && node.morphTargetDictionary) {
//             //         avatarMeshesWithMorphTargets.push(node);
//             //         for (const [key, value] of Object.entries(node.morphTargetDictionary)) {
//             //             visemeMorphTargetIndices[key.toLowerCase()] = value;
//             //         }
//             //     }
//             // });
//             // console.log("Meshes with morph targets:", avatarMeshesWithMorphTargets);
//             // console.log("Viseme Morph Target Indices:", visemeMorphTargetIndices);
//         },
//         function (xhr) {
//             const progress = (xhr.loaded / xhr.total * 100);
//             document.getElementById('info').textContent = `Loading: ${progress.toFixed(2)}%`;
//             console.log('Loading ' + progress + '% of model');
//         },
//         function (error) {
//             console.error('An error occurred while loading the model:', error);
//             document.getElementById('info').textContent = 'Error loading avatar!';
//         }
//     );

//     // Handle window resize
//     window.addEventListener('resize', () => {
//         const width = container.clientWidth;
//         const height = container.clientHeight;
//         camera.aspect = width / height;
//         camera.updateProjectionMatrix();
//         renderer.setSize(width, height);
//     });
// }


// function animate() {
//     requestAnimationFrame(animate);

//     // Removed: Lip-sync logic
//     // if (audio && audio.isPlaying && lipSyncData.length > 0) {
//     //     const currentTime = audio.context.currentTime - audio.startTime;
//     //     while (currentPhonemeIndex < lipSyncData.length &&
//     //            lipSyncData[currentPhonemeIndex].start_time <= currentTime) {
//     //         currentPhonemeIndex++;
//     //     }
//     //     if (currentPhonemeIndex > 0) {
//     //         const currentPhoneme = lipSyncData[currentPhonemeIndex - 1];
//     //         applyPhonemeToAvatar(currentPhoneme.phoneme);
//     //     } else {
//     //         applyPhonemeToAvatar('');
//     //     }
//     // } else if (audio && !audio.isPlaying) {
//     //     resetMorphTargets();
//     // }

//     renderer.render(scene, camera);
// }

// // Removed: Lip-sync related functions
// // function applyPhonemeToAvatar(phoneme) {
// //     resetMorphTargets();
// //     let viseme = getVisemeForPhoneme(phoneme);
// //     if (viseme && visemeMorphTargetIndices.hasOwnProperty(viseme)) {
// //         const morphIndex = visemeMorphTargetIndices[viseme];
// //         avatarMeshesWithMorphTargets.forEach(mesh => {
// //             if (mesh.morphTargetInfluences && mesh.morphTargetInfluences[morphIndex] !== undefined) {
// //                 mesh.morphTargetInfluences[morphIndex] = 1.0;
// //             }
// //         });
// //     }
// // }

// // function resetMorphTargets() {
// //     avatarMeshesWithMorphTargets.forEach(mesh => {
// //         if (mesh.morphTargetInfluences) {
// //             for (let i = 0; i < mesh.morphTargetInfluences.length; i++) {
// //                 mesh.morphTargetInfluences[i] = 0;
// //             }
// //         }
// //     });
// // }

// // function getVisemeForPhoneme(phoneme) {
// //     phoneme = phoneme.toLowerCase();
// //     if (phoneme === 'p' || phoneme === 'b' || phoneme === 'm') return 'viseme_PP';
// //     if (phoneme === 'f' || phoneme === 'v') return 'viseme_FF';
// //     if (phoneme === 'th' || phoneme === 'dh') return 'viseme_TH';
// //     if (phoneme === 's' || phoneme === 'z' || phoneme === 'sh' || phoneme === 'zh' || phoneme === 'ch' || phoneme === 'jh') return 'viseme_SS';
// //     if (phoneme === 't' || phoneme === 'd' || phoneme === 'n' || phoneme === 'l') return 'viseme_DD';
// //     if (phoneme === 'k' || phoneme === 'g' || phoneme === 'ng') return 'viseme_KK';
// //     if (phoneme === 'r') return 'viseme_RR';
// //     if (phoneme === 'w' || phoneme === 'wh') return 'viseme_WW';
// //     if (phoneme === 'y' || phoneme === 'ih' || phoneme === 'iy') return 'viseme_IH';
// //     if (phoneme === 'aa' || phoneme === 'ao') return 'viseme_AA';
// //     if (phoneme === 'ah' || phoneme === 'uh' || phoneme === 'er') return 'viseme_AH';
// //     if (phoneme === 'eh') return 'viseme_EH';
// //     if (phoneme === 'aw') return 'viseme_AW';
// //     if (phoneme === 'ow' || phoneme === 'uw') return 'viseme_OW';
// //     if (phoneme === 'oy') return 'viseme_OY';
// //     return 'viseme_sil';
// // }

// init();
// animate();