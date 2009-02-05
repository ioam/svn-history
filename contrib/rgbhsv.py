"""
Work in progress. Optimized functions to convert between rgb and hsv.
Need to check input and output types are compatible with standard
colorsys functions.


$Id: rgbhsv.py 31 2008-12-15 11:40:30Z v1cball $
"""


from topo.misc.inlinec import inline
import numpy


def rgb_to_hsv_array(r,g,b):
    """
    Equivalent to colorsys.rgb_to_hsv, except:
      * acts on arrays of red, green, and blue pixels
      * works correctly when r,g,b are of type int
      * returns arrays of type numpy.float32 for hue,saturation,and value
    """
    assert r.dtype==g.dtype==b.dtype==numpy.int32
    
    from colorsys import rgb_to_hsv
    rows,cols=r.shape
    h=numpy.zeros((rows,cols),dtype=numpy.float32)
    v=numpy.zeros((rows,cols),dtype=numpy.float32)
    s=numpy.zeros((rows,cols),dtype=numpy.float32)
    for i in range(rows):
        for j in range(cols):
            # float() necessary because division in colorsys.rgb_to_hsv()
            # will be integer division unless inputs are floats
            h[i,j],s[i,j],v[i,j]=rgb_to_hsv(float(r[i,j]),
                                            float(g[i,j]),
                                            float(b[i,j]))
    return h,s,v


def hsv_to_rgb_array(h,s,v):
    """
    Equivalent to colorsys.hsv_to_rgb, except:
      * acts on arrays of hue, saturation, and value
      * returns arrays of type numpy.int32 for red, green, and blue.
    """
    from colorsys import hsv_to_rgb
    rows,cols = h.shape
    r = numpy.zeros((rows,cols),dtype=numpy.int32)
    g = numpy.zeros((rows,cols),dtype=numpy.int32)
    b = numpy.zeros((rows,cols),dtype=numpy.int32)
    for i in range(rows):
        for j in range(cols):
            red,grn,blu=hsv_to_rgb(h[i,j],s[i,j],v[i,j])
            r[i,j]=int(round(red,0))
            g[i,j]=int(round(grn,0))
            b[i,j]=int(round(blu,0))
    return r,g,b



def rgb_to_hsv_array_opt(red,grn,blu):
    """Supposed to be equivalent to rgb_to_hsv_array()."""
    shape = red.shape
    assert grn.shape==blu.shape==shape
    
    hue = numpy.zeros(shape,dtype=numpy.float32)
    sat = numpy.zeros(shape,dtype=numpy.float32)
    val = numpy.zeros(shape,dtype=numpy.float32)

    code = """
//// MIN3,MAX3 macros from
// http://en.literateprograms.org/RGB_to_HSV_color_space_conversion_(C)
#define MIN3(x,y,z)  ((y) <= (z) ? \
                         ((x) <= (y) ? (x) : (y)) \
                     : \
                         ((x) <= (z) ? (x) : (z)))

#define MAX3(x,y,z)  ((y) >= (z) ? \
                         ((x) >= (y) ? (x) : (y)) \
                     : \
                         ((x) >= (z) ? (x) : (z)))
////

for (int i=0; i<Nred[0]; ++i) {
    for (int j=0; j<Nred[1]; ++j) {

        // translation of Python's colorsys.rgb_to_hsv()

        int r=RED2(i,j);
        int g=GRN2(i,j);
        int b=BLU2(i,j);

        float minc=MIN3(r,g,b); 
        float maxc=MAX3(r,g,b); 

        VAL2(i,j)=maxc;

        if(minc==maxc) {
            HUE2(i,j)=0.0;
            SAT2(i,j)=0.0;
        } else {
            float delta=maxc-minc; 
            SAT2(i,j)=delta/maxc;

            float rc=(maxc-r)/delta;
            float gc=(maxc-g)/delta;
            float bc=(maxc-b)/delta;

            if(r==maxc)
                HUE2(i,j)=bc-gc;
            else if(g==maxc)
                HUE2(i,j)=2.0+rc-bc;
            else
                HUE2(i,j)=4.0+gc-rc;

            HUE2(i,j)=(HUE2(i,j)/6.0);

            if(HUE2(i,j)<0)
                HUE2(i,j)+=1;
            //else if(HUE2(i,j)>1)
            //    HUE2(i,j)-=1;

        }

    }
}

"""
    inline(code, ['red','grn','blu','hue','sat','val'], local_dict=locals())
    return hue,sat,val



def hsv_to_rgb_array_opt(hue,sat,val):
    """Supposed to be equivalent to hsv_to_rgb_array()."""
    shape = hue.shape
    assert sat.shape==val.shape==shape
    
    red = numpy.zeros(shape,dtype=numpy.int32)
    grn = numpy.zeros(shape,dtype=numpy.int32)
    blu = numpy.zeros(shape,dtype=numpy.int32)

    code = """
for (int i=0; i<Nhue[0]; ++i) {
    for (int j=0; j<Nhue[1]; ++j) {

        // translation of Python's colorsys.hsv_to_rgb() using parts
        // of code from
        // http://www.cs.rit.edu/~ncs/color/t_convert.html
        float h=HUE2(i,j);
        float s=SAT2(i,j);
        float v=VAL2(i,j);

	float r,g,b;
        
	if(s==0) 
            r=g=b=v;
	else {
            int i=(int)floor(h*6.0);
            if(i<0) i=0;
            
            float f=(h*6.0)-i;
            float p=v*(1.0-s);
            float q=v*(1.0-s*f);
            float t=v*(1.0-s*(1-f));

            switch(i) {
                case 0:
                    r = v;
                    g = t;
                    b = p;
                    break;
                case 1:
                    r = q;
                    g = v;
                    b = p;
                    break;
                case 2:
                    r = p;
                    g = v;
                    b = t;
                    break;
                case 3:
                    r = p;
                    g = q;
                    b = v;
                    break;
                case 4:
                    r = t;
                    g = p;
                    b = v;
                    break;
                case 5:
                    r = v;
                    g = p;
                    b = q;
                    break;
            }
        }
        RED2(i,j)=(int)round(r);
        GRN2(i,j)=(int)round(g);
        BLU2(i,j)=(int)round(b);
    }
}
"""
    inline(code, ['red','grn','blu','hue','sat','val'], local_dict=locals())
    return red,grn,blu






if __name__=='__main__' or __name__=='__mynamespace__':

    imagepath = 'images/f2/MERRY0006.tif'

    import Image
    import numpy

    from numpy.testing import assert_array_almost_equal,\
                              assert_array_equal

    im = Image.open(imagepath)
    R,G,B = im.split()

    # PIL 1.1.6 would simplify this
    R = numpy.array(R.getdata(),dtype=numpy.int32)
    R.shape = im.size
    G = numpy.array(G.getdata(),dtype=numpy.int32)
    G.shape = im.size
    B = numpy.array(B.getdata(),dtype=numpy.int32)
    B.shape = im.size

    ## test rgb_to_hsv
    H,S,V = rgb_to_hsv_array_opt(R,G,B)
    h,s,v = rgb_to_hsv_array(R,G,B)
    assert_array_almost_equal(h,H,decimal=6)
    assert_array_almost_equal(s,S,decimal=6)
    assert_array_almost_equal(v,V,decimal=6)


    ## test hsv_to_rgb 
    R2,G2,B2 = hsv_to_rgb_array_opt(H,S,V)
    r2,g2,b2 = hsv_to_rgb_array(H,S,V)
    # test python implementations
    assert_array_equal(r2,R)
    assert_array_equal(g2,G)
    assert_array_equal(b2,B)
    # test C implementation
    assert_array_equal(R2,R)
    assert_array_equal(G2,G)
    assert_array_equal(B2,B)


    print "OK"






