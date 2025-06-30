

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, avatar;
let controls; 
// let audio, audioLoader;
// let lipSyncData = [];
// let currentPhonemeIndex = 0;
// let avatarMeshesWithMorphTargets = []; // To store meshes that have morph targets

// function loadGLB(path) {
//     if (avatar) {
//         scene.remove(avatar);
//     }
// }

function loadGLB(path) {
    if (avatar) {
        scene.remove(avatar);
    }

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
    const defaultGLBPath = '/static/models/har.glb';
    const cacheBustedPath = `${defaultGLBPath}?t=${Date.now()}`;

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

