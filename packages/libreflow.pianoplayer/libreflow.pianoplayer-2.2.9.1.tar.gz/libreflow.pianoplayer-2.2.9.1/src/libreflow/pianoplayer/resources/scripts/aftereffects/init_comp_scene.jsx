
/**
 * Lazy function to print a message in the javascript console
 * as I kept forgetting the syntax for writeln() ...
 */
 function print(msg){
    $.writeln(msg)
}

// FROM Smart Import.jx
function testForSequence(files) {
    var searcher = new RegExp("[0-9]+");
    var movieFileSearcher = new RegExp("(mov|avi|mpg)$", "i");
    var parseResults = new Array;

    // Test that we have a sequence. Stop parsing after 10 files.
    for (x = 0;
        (x < files.length) & x < 10; x++) {
        var movieFileResult = movieFileSearcher.exec(files[x].name);
        if (!movieFileResult) {
            var currentResult = searcher.exec(files[x].name);
            // Regular expressions return null if no match was found.
            // Otherwise, they return an array with the following information:
            // array[0] = the matched string.
            // array[1..n] = the matched capturing parentheses.

            if (currentResult) { // We have a match -- the string contains numbers.
                // The match of those numbers is stored in the array[1].
                // Take that number and save it into parseResults.
                parseResults[parseResults.length] = currentResult[0];
            } else {
                parseResults[parseResults.length] = null;
            }
        } else {
            parseResults[parseResults.length] = null;
        }
    }
    // If all the files we just went through have a number in their file names,
    // assume they are part of a sequence and return the first file.

    var result = null;
    for (j = 0; j < parseResults.length; ++j) {
        if (parseResults[j]) {
            if (!result) {
                result = files[j];
            }
        } else {
            // In this case, a file name did not contain a number.
            result = null;
            break;
        }
    }

    return result;
}

function importSafeWithError(importOptions) {
    try {
        return app.project.importFile(importOptions);
    } catch (error) {
        alert(error.toString() + importOptions.file.fsName, scriptName);
    }
}

function getFolder(path, create) {
    path = path.replace(/^\/+/, "");
    path = path.replace(/\/+$/, "");
    create = (typeof create !== 'undefined') ?  create : false;

    var folderNames = path.split("/");

    if (folderNames.length == 0)
        return null;

    var folderName = folderNames[0];
    var folder = null;
    var parent = null;

    for (var i = 1;  i <= app.project.items.length; i++) {
        if (app.project.items[i].name == folderName && app.project.items[i] instanceof FolderItem) {
            parent = app.project.items[i];
            break;
        }
    }

    if (parent == null && create) {
        parent = app.project.items.addFolder(folderName);
    }

    folder = parent;

    for (var i = 1; folder !== null && i < folderNames.length; i++) {
        folder = null;

        for (var j = 1; j <= parent.numItems; j++) {
            if (parent.items[j].name == folderNames[i] && parent.items[j] instanceof FolderItem) {
                parent = parent.items[j];
                folder = parent;
                break;
            }
        }
        if (folder == null && create) {
            folder = app.project.items.addFolder(folderNames[i]);
            folder.parentFolder = parent;
            parent = folder;
        }
    }

    return folder;
}

function getComp(compName) {
    comp = null;

    for (var i = 1; i <= app.project.numItems; i++) {
        if (app.project.items[i].name == compName && app.project.items[i] instanceof CompItem) {
            comp = app.project.items[i];
            break;
        }
    }

    return comp;
}

/**
 * Update the duration of the input composition, and recursively that
 * of all compositions and footages it contains.
 */
 function updateCompDuration(comp, duration) {
    comp.duration = duration;

    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);
        
        // Update in and out points of footages since their duration is read-only
        // From https://stackoverflow.com/a/41543354
        if (layer.source instanceof CompItem) {     // Composition
            updateCompDuration(layer.source, duration);
        } else {                                    // Footage
            layer.outPoint = layer.inPoint + duration;
        }
    }
}

function openScene(scenePath) {
    if (app.project !== null && (app.project.file !== null || app.project.dirty)) {
        //var close = confirm("AfterEffects must be closed before the scene can be initialised. Save and close the current project ?");
        var close = confirm(app.project.file.name);
        if (close)
            app.project.close(CloseOptions.SAVE_CHANGES);
        else
            throw new Error();
    }

    scene = File(scenePath);
    app.open(scene);
}

function setupScene(scenePath, masterCompName, width, height, duration) {
    if (app.project !== null && (app.project.file != null || app.project.dirty)) {
        var close = confirm("AfterEffects must be closed before the scene can be initialised. Save and close the current project ?");
        if (close)
            app.project.close(CloseOptions.SAVE_CHANGES);
        else
            throw new Error();
    }

    scene = File(scenePath);
    app.open(scene);

    app.project.bitsPerChannel = 16;
    app.project.workingSpace = "sRGB IEC61966-2.1";
    app.project.workingGamma = "2.2";
    app.project.GpuAccelType = GpuAccelType.SOFTWARE;

    // Create master composition
    var masterComp = app.project.items.addComp(masterCompName, width, height, 1, duration/24, 24);
    masterComp.label = 9;
}

function saveScene() {
    app.project.save();
}

function updateBackgroundSources(backgroundPath, backgroundVersion, duration) {
    // Create an empty folder
    var bgSourcesFolder = getFolder("02 - SOURCES/BG/" + backgroundVersion);

    if (bgSourcesFolder !== null)
        return null; // background version already exists
    
    bgSourcesFolder = getFolder("02 - SOURCES/BG/" + backgroundVersion, true);

    // Add background scene as composition
    var file = File(backgroundPath);
    var bgSourceCompName = file.name.substring(0, file.name.lastIndexOf('.'));
    var io = new ImportOptions(file);
    io.importAs = ImportAsType.COMP;
    var bgSourceComp = app.project.importFile(io);
    bgSourceComp.parentFolder = bgSourcesFolder;
    bgSourceComp.label = 9;

    updateCompDuration(bgSourceComp, duration); // Update duration of composition and all its footages

    // Add background layers
    bgLayersFolder = getFolder(bgSourceComp.name + " Calques");
    bgSourceComp.name = bgSourceCompName;
    bgLayersFolder.name = bgSourceCompName;

    if (bgLayersFolder !== null) {
        bgLayersFolder.parentFolder = bgSourcesFolder;
        bgLayersFolder.label = 9;
    }

    return bgSourceComp;
}

function importBackground(backgroundPath, backgroundVersion, width, height, duration, masterCompName) {
    // Import background sources
    var bgSourceComp = updateBackgroundSources(backgroundPath, backgroundVersion, duration/24);

    // Create a composition which will hold the original background layer
    var composFolder = getFolder("01 - COMPOS", true);
    bgComp = composFolder.items.addComp("BACKGROUND", bgSourceComp.width, bgSourceComp.height, 1, duration/24, 24);
    bgComp.label = 9;

    var masterComp = getComp(masterCompName);
    var backgroundLayer = masterComp.layers.add(bgComp);
    backgroundLayer.property("scale").setValue([71.0, 71.0, 0.0]);
    backgroundLayer.moveToEnd();

    // Filter layers
    var bgLayers = [];

    for (var i = bgSourceComp.numLayers; i > 0; i--) {
        var bgLayer = bgSourceComp.layers[i];

        if (bgLayer.name.match(/\s*(EXTRA.*|BG)\s*/)) {
            // Main layer
            bgLayer.label = 9;
            bgLayer.copyToComp(bgComp);
        } else {
            if (bgLayer.name.match(/.*(CAMERA|LABEL|BRIEFING|DIALOGUE).*/)) {
                // Guide layer
                bgLayer.guideLayer = true;
            }
            bgLayer.label = 0;
            bgLayers.push(bgLayer);
        }
    }

    // Update master composition

    if (masterComp !== null) {
        // Deselect existing layers
        for (var i = 1; i <= masterComp.numLayers; i++)
            masterComp.layers[i].selected = false;
        
        // Copy guide layers
        for (var i = 0; i < bgLayers.length; i++) {
            bgLayers[i].copyToComp(masterComp);

            bgLayerCopy = masterComp.layer(1);
            bgLayerCopy.enabled = false;
            bgLayerCopy.property("position").setValue([width/2.0, height/2.0, 0.0]);
            bgLayerCopy.property("scale").setValue([71.0, 71.0, 0.0]);
        }
    }
}

function importAnimatic(animaticPath, masterCompName) {
    var file = File(animaticPath);
    var io = new ImportOptions(file);
    var animaticFile = app.project.importFile(io);
    animaticFile.parentFolder = getFolder("02 - SOURCES", true);

    var masterComp = getComp(masterCompName);

    if (masterComp !== null) {
        antcLayer = masterComp.layers.add(animaticFile);
        antcLayer.name = "ANIMATIC";
        antcLayer.label = 0;
        antcLayer.guideLayer = true;
        antcLayer.enabled = false;
        antcLayer.audioEnabled = false;
        antcLayer.property("anchorPoint").setValue([0.0, 0.0, 0.0]);
        antcLayer.property("position").setValue([0.0, 0.0, 0.0]);
        antcLayer.property("scale").setValue([71.0, 71.0, 0.0]);
        antcLayer.moveToBeginning();
    }
}

function importVideoRef(videoRefPath, masterCompName) {
    var file = File(videoRefPath);
    var io = new ImportOptions(file);
    var refFile = app.project.importFile(io);
    refFile.parentFolder = getFolder("02 - SOURCES", true);

    var masterComp = getComp(masterCompName);

    if (masterComp !== null) {
        refLayer = masterComp.layers.add(refFile);
        refLayer.name = "REF";
        refLayer.label = 0;
        refLayer.guideLayer = true;
        refLayer.enabled = false;
        refLayer.audioEnabled = false;
        refLayer.property("anchorPoint").setValue([0.0, 0.0, 0.0]);
        refLayer.property("position").setValue([0.0, 0.0, 0.0]);
        refLayer.property("scale").setValue([71.0, 71.0, 0.0]);
        refLayer.moveToBeginning();
    }
}

function importAudio(audioPath, masterCompName) {
    var file = File(audioPath);
    var io = new ImportOptions(file);
    var audioFile = app.project.importFile(io);
    audioFile.parentFolder = getFolder("02 - SOURCES", true);
    audioFile.label = 12;

    var masterComp = getComp(masterCompName);

    if (masterComp !== null) {
        audioLayer = masterComp.layers.add(audioFile);
        audioLayer.moveToEnd();
    }
}

function updateLayerSources(layerFolders, layersVersion) {
    // Create an empty folder
    var layersFolder = getFolder("02 - SOURCES/ANIM/" + layersVersion);

    if (layersFolder !== null)
        return null; // background version already exists

    layersFolder = getFolder("02 - SOURCES/ANIM/" + layersVersion, true);

    // Import image sequences
    var fileSequences = [];

    for (var i = 0; i < layerFolders.length; i++) {
        var sequenceFolders = layerFolders[i];
        var sequences = [];

        // Import image sequences
        for (var j = 0; j < sequenceFolders.length; j++) {
            // Import sequence
            var files = Folder(sequenceFolders[j]).getFiles();
            var sequenceStartFile = testForSequence(files);
            var io = new ImportOptions(sequenceStartFile);
            io.sequence = true;
            var importedFile = importSafeWithError(io);

            // Move sequence into anim source folder
            importedFile.parentFolder = layersFolder;
            importedFile.mainSource.conformFrameRate = 24;
            importedFile.label = 11;

            sequences.push(importedFile);
        }

        fileSequences.push(sequences);
    }

    return fileSequences;
}

function importLayers(layerLabels, layerFolders, layersVersion, width, height, duration, masterCompName) {
    // Import layer sources
    var fileSequences = updateLayerSources(layerFolders, layersVersion);
    var layersComposFolder = getFolder("01 - COMPOS/ANIM", true);
    var layersCompos = [];

    for (var i = 0; i < layerLabels.length; i++) {
        var layersComp = layersComposFolder.items.addComp(layerLabels[i], width, height, 1, duration/24, 24);
        layersComp.label = 11;

        var sequences = fileSequences[i];

        // Import image sequences
        for (var j = 0; j < sequences.length; j++) {
            var animLayer = layersComp.layers.add(sequences[j]);
            animLayer.label = 11;
        }

        layersCompos.push(layersComp);
    }

    var masterComp = getComp(masterCompName);

    if (masterComp !== null) {
        // Add new layer compositions to master
        for (i = layersCompos.length - 1; i >= 0; i--) {
            masterComp.layers.add(layersCompos[i]);
        }
    }
}

// initialiseShot("TS_test", "c999", "s010", 4096, 1743, 106)