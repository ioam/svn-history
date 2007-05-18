"""
Face Generator based on shapes and textures stored in hdf5 database.
"""


from numpy.oldnumeric import array, Float, sum, ravel, ones, zeros, double
from topo.base.parameterclasses import Filename, Number
from topo.misc.numbergenerators import UniformRandomInt, UniformRandom
from topo.base.parameterclasses import DynamicNumber

from tables import file, array
from topo.patterns.image import Image, PatternSampler


class FaceSpace2D(Image):
    """
    Presents images from a set indexed in two dimensions: caricaturization and identity.

    Used for testing how face-selective responses depend on
    differences from a mean face and on individual identities.

    Requires a database in hdf5 format storing modelled shapes
    and textures of 37 faces from IMM Face Database:
    
    http://www2.imm.dtu.dk/pubdb/views/publication_details.php?id=922
    
    The active appearance model (AAM) is then used to build
    models of each faces as well as the mean face, using the
    program AAMBuilding:
    
    http://sourceforge.net/projects/aambuilding
    
    Morphes between any two face identities (incluidng the mean
    face) can be generated. Over-caricaturization (above 1.0)
    and anti-faces (below 0) can be obtained.
    
    Parameters:
    
    identity_ref: reference face (i.e. the morph starting point)
    For a mean-face centered trajectory, mean face (0) is used.
    
    identity_target: target face (i.e. the morph target point)
    Given the database, it ranges [0, 37]
    
    caricaturization_shape: the degree of linear transformation
    of the generated face shape. 0 means the same shape as the
    reference face, 1.0 means the same shape as the target face,
    Values above 1.0 means over-caricaturization and below 0
    means anti-faces. It is possible to specify an arbitary
    caricaturization, however values above 1.5 and below -1.5
    are not visually useful.
    
    caricaturization_texture: the degree of linear transformation
    of the generated face texture. Typically this should be the
    same value as caricaturization_shape. 0 means the same
    texture (appearance) as the reference face, and 1.0 means
    te same texture as the target face. Applying different value
    of this parameter with caricaturization_shape may result in
    strange face. For example, Setting this to 0.5 while setting
    caricaturization_shape to 1.0 produces a face with same
    'layout' as the target face but still half like the
    reference face.
    """

    identity_target = DynamicNumber(default = UniformRandomInt(lbound = 0, ubound = 37, seed = 94),
                             precedence = 0.20, doc = """
        Number specifying which person's face should be used as target,
        i.e. the morph target point.""")

    identity_ref = DynamicNumber(default = UniformRandomInt(lbound = 0, ubound = 37, seed = 21),
                             precedence = 0.20, doc = """
        Number specifying which person's face should be used as reference,
        i.e. the morph starting point.""")

    caricaturization_shape = DynamicNumber(default = UniformRandom(lbound = -1.5, ubound = 1.5, seed = 43),                                      precedence = 0.20, doc = """
        Amount of caricaturization of the face shape, on a scale with 0 being
        the reference face shape and 1.0 being the target face shape. Values
        above 1.0 represent exaggerations (caricatures), and those below 1.0
        represent averaged faces. Values below 0.0 represent 'anti-faces'.""")

    caricaturization_texture = DynamicNumber(default = UniformRandom(lbound = -1.5, ubound = 1.5, seed = 18),                                      precedence = 0.20, doc = """
        Amount of caricaturization of the face texture. Typically this value
        is the same as caricaturization_shape.""")

    imm_face_db = Filename(default='facedb/aam_fit_data.h5',precedence=0.9,doc="""
        String specification for the filename of the IMM face database with
        built AAM model shapes and textures.""")


    def __init__(self, **params):
        """
        """
        super(FaceSpace2D,self).__init__(**params)
        # Flag indicating whether the big db has been loaded. It should be loaded only once.
        self.db_loaded = False

    def __generate_face_sampler(self, identity_target, identity_ref, c_shape, c_texture, whole_image_output_fn):
        """
        Generate a face PatternSampler based on the supplied parameters.   

        The PatternSampler is generated to grayscale.
        """
        shape_target_template = self.shapes_template[identity_target]
        shape_ref_template = self.shapes_template[identity_ref]
        shape_target_warp = self.shapes_warp[identity_target]
        exec(compile('texture_target = self.texture_' + str(identity_target), '<string>', 'exec'))
        shape_ref_warp = self.shapes_warp[identity_ref]
        exec(compile('texture_ref = self.texture_' + str(identity_ref), '<string>', 'exec'))
        triangles = self.triangles
        image_array = self.__aam_fit(shape_target_template, shape_ref_template, c_shape, c_texture,
                                shape_target_warp, texture_target, shape_ref_warp, texture_ref,
                                triangles)
        # The slice of [60:350] aims at cropped out the image part above eyebrow.
        self.ps = PatternSampler(image_array[60 : 350], whole_image_output_fn)
        
    def __load_db(self, imm_face_db):
        h5file = file.openFile(imm_face_db, "r")
        for identity in range(0, 38):
            exec(compile('self.texture_' + str(identity) + ' = h5file.root.textures.f' + str(identity) + '.read()', '<string>', 'exec'))
        self.shapes_template = h5file.root.shapes_template.read()
        self.shapes_warp = h5file.root.shapes_warp.read()
        self.triangles = h5file.root.triangles.read()
        h5file.close()
        self.db_loaded = True


    def __aam_fit(self, shape_target_template, shape_ref_template, c_shape, c_texture,
                  shape_target_warp, texture_target, shape_ref_warp, texture_ref,
                  triangles):

        """
        shape_target_template: coords in 640x480, registered w/ shape_ref_template,
                               morph target
        shape_ref_template: coords in 640x480, morph reference
        c_shape: caricaturization of shape
        c_texture: caricaturization of texture
        shape_target_warp: coords ~ 210x210, unregistered & cropped version of
                           shape_target_template, morph target
        texture_target: x, y, belonging triangle and strength of each face pixel,
                        corresponding to coords of key points in shape_target_warp
        shape_ref_warp: coords ~ 210x210, unregistered & cropped version of
                        shape_ref_template, morph reference
        texture_ref: x, y, belonging triangle and strength of each face pixel,
                     corresponding to coords of key points in shape_ref_warp
        triangles: key point id of three angles of 95 triangles
        
        face_fill_radius: radius to fill the gap around each pixel online
        do_post_interp: proceed post building interpolation (horizontal)
        bg_color: background color of this face image

        This program displays the linear transformed registered face comb
        (shape_target_template and shape_ref_template) and fills the new shape
        with linear transformed textures. The coords in texture_target and
        texture_ref are affine transformed into the new shape coords.
        """
        
        face_fill_radius = 1
        do_post_interp = True;
        bg_color = 0.5;

        face_img_ref = zeros((351, 351), double) + bg_color

        for i in range(len(texture_ref)):

            tri = int(texture_ref[i][2]);

            tri_r = triangles[tri][0]
            tri_s = triangles[tri][1]
            tri_t = triangles[tri][2]
            x_r = shape_ref_warp[tri_r * 2]
            y_r = shape_ref_warp[tri_r * 2 + 1]
            x_s = shape_ref_warp[tri_s * 2]
            y_s = shape_ref_warp[tri_s * 2 + 1]
            x_t = shape_ref_warp[tri_t * 2]
            y_t = shape_ref_warp[tri_t * 2 + 1]
            x_at = texture_ref[i][0]
            y_at = texture_ref[i][1]
            at_denominator = x_s * y_t - x_r * y_t - x_s * y_r - y_s * x_t + y_r * x_t + y_s * x_r
            at_alpha = (x_s * y_t - y_s * x_t - x_at * y_t + y_at * x_t - y_at * x_s + x_at * y_s) / float(at_denominator)
            at_beta = (x_at * y_t - x_r * y_t - x_at * y_r - y_at * x_t + y_r * x_t + y_at * x_r) / float(at_denominator)
            at_gamma = (y_at * x_s - y_r * x_s - y_at * x_r - x_at * y_s + x_r * y_s + x_at * y_r) / float(at_denominator)

            x_r1 = shape_ref_template[tri_r * 2]
            y_r1 = shape_ref_template[tri_r * 2 + 1]
            x_s1 = shape_ref_template[tri_s * 2]
            y_s1 = shape_ref_template[tri_s * 2 + 1]
            x_t1 = shape_ref_template[tri_t * 2]
            y_t1 = shape_ref_template[tri_t * 2 + 1]

            x_trans = int(round(at_alpha * x_r1 + at_beta * x_s1 + at_gamma * x_t1))
            y_trans = int(round(at_alpha * y_r1 + at_beta * y_s1 + at_gamma * y_t1))
            face_img_ref[y_trans][x_trans] = texture_ref[i][3];

            for temp_i in range(x_trans - face_fill_radius, x_trans + face_fill_radius + 1):
                for temp_j in range(y_trans - face_fill_radius, y_trans + face_fill_radius + 1):
                    if face_img_ref[temp_j][temp_i] == bg_color:
                        face_img_ref[temp_j][temp_i] = texture_ref[i][3]


        shape_target_template = (shape_ref_template + (shape_target_template - shape_ref_template) * c_shape).round()

        face_img = zeros((351, 351), double) + bg_color

        for i in range(len(texture_target)):

            tri_r = triangles[int(texture_target[i][2])][0]
            tri_s = triangles[int(texture_target[i][2])][1]
            tri_t = triangles[int(texture_target[i][2])][2]
            x_r = shape_target_warp[tri_r * 2]
            y_r = shape_target_warp[tri_r * 2 + 1]
            x_s = shape_target_warp[tri_s * 2]
            y_s = shape_target_warp[tri_s * 2 + 1]
            x_t = shape_target_warp[tri_t * 2]
            y_t = shape_target_warp[tri_t * 2 + 1]
            x_at = texture_target[i][0]
            y_at = texture_target[i][1]
            at_denominator = x_s * y_t - x_r * y_t - x_s * y_r - y_s * x_t + y_r * x_t + y_s * x_r
            at_alpha = (x_s * y_t - y_s * x_t - x_at * y_t + y_at * x_t - y_at * x_s + x_at * y_s) / float(at_denominator)
            at_beta = (x_at * y_t - x_r * y_t - x_at * y_r - y_at * x_t + y_r * x_t + y_at * x_r) / float(at_denominator)
            at_gamma = (y_at * x_s - y_r * x_s - y_at * x_r - x_at * y_s + x_r * y_s + x_at * y_r) / float(at_denominator)

            x_r1 = shape_target_template[tri_r * 2]
            y_r1 = shape_target_template[tri_r * 2 + 1]
            x_s1 = shape_target_template[tri_s * 2]
            y_s1 = shape_target_template[tri_s * 2 + 1]
            x_t1 = shape_target_template[tri_t * 2]
            y_t1 = shape_target_template[tri_t * 2 + 1]

            x_ref_r = shape_ref_template[tri_r * 2]
            y_ref_r = shape_ref_template[tri_r * 2 + 1]
            x_ref_s = shape_ref_template[tri_s * 2]
            y_ref_s = shape_ref_template[tri_s * 2 + 1]
            x_ref_t = shape_ref_template[tri_t * 2]
            y_ref_t = shape_ref_template[tri_t * 2 + 1]

            x_trans = int(round(at_alpha * x_r1 + at_beta * x_s1 + at_gamma * x_t1))
            y_trans = int(round(at_alpha * y_r1 + at_beta * y_s1 + at_gamma * y_t1))
            x_ref_trans = int(round(at_alpha * x_ref_r + at_beta * x_ref_s + at_gamma * x_ref_t))
            y_ref_trans = int(round(at_alpha * y_ref_r + at_beta * y_ref_s + at_gamma * y_ref_t))
            face_img[y_trans][x_trans] = face_img_ref[y_ref_trans][x_ref_trans] + c_texture * (texture_target[i][3] - face_img_ref[y_ref_trans][x_ref_trans])

            for temp_i in range(x_trans - face_fill_radius, x_trans + face_fill_radius + 1):
                for temp_j in range(y_trans - face_fill_radius, y_trans + face_fill_radius + 1):
                    if face_img[temp_j][temp_i] == bg_color:
                        # mf(temp_j, temp_i) = sum(sum(mf(temp_j - 1 : temp_j + 1, temp_i - 1 : temp_i + 1))) ./ 8;
                        face_img[temp_j][temp_i] = face_img[y_trans][x_trans]

        if do_post_interp:

            height = len(face_img)
            width = len(face_img[0])
            bg_color = 0.5

            for row in range(height):

                no_interp = True
                interp_start = -1
                interp_end = 0

                for i in range(width):
 
                        if face_img[i][row] != bg_color and no_interp: no_interp = False

                        if face_img[i][row] != bg_color and not no_interp and interp_start != -1 and interp_end  == -1:
                            interp_end = i
                            interval = (face_img[interp_end][row] - face_img[interp_start][row]) / abs(interp_end - interp_start)
                            for j in range(interp_start + 1, interp_end):
                                face_img[j][row] = face_img[j - 1][row] + interval;
                            interp_start = -1

                        if face_img[i][row] == bg_color and not no_interp and interp_start == -1 and interp_end != -1:
                            interp_start = i - 1
                            interp_end = -1

        return face_img


    def function(self,**params):
        identity_target = params.get('identity_target', self.identity_target)
        identity_ref = params.get('identity_ref', self.identity_ref)
        caricaturization_shape = params.get('caricaturization_shape', self.caricaturization_shape)
        caricaturization_texture = params.get('caricaturization_texture', self.caricaturization_texture)
        imm_face_db = params.get('imm_face_db', self.imm_face_db)
        db_loaded = params.get('db_loaded', self.db_loaded)
        if not db_loaded:
            self.__load_db(imm_face_db)

        xdensity = params.get('xdensity', self.xdensity)
        ydensity = params.get('ydensity', self.ydensity)
        x        = params.get('pattern_x',self.pattern_x)
        y        = params.get('pattern_y',self.pattern_y)
        filename = params.get('filename',self.filename)
        size_normalization = params.get('scaling',self.size_normalization)
        whole_image_output_fn = params.get('whole_image_output_fn',self.whole_image_output_fn)

        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        self.__generate_face_sampler(identity_target, identity_ref,
                                     caricaturization_shape, caricaturization_texture,
                                     whole_image_output_fn)

        return self.ps(x,y,float(xdensity),float(ydensity),size_normalization,float(width),float(height))

