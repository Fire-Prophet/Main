const express = require('express');
const router = express.Router();
const multer = require('multer');
const { uploadModel } = require('../../controllers/ai/uploadController');

const upload = multer({ dest: 'uploads/' });

router.post('/', upload.single('model'), uploadModel);

module.exports = router;
