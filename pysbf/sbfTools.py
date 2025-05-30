import uuid, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import datetime
import ipywidgets as widgets


from .utils import *

##############################################################
class SBFobject:

    x0 = 0
    y0 = 0
    a = 1
    b = 1
    name = ""
    R = 1  # Kron Radius
    angle = 0  # Position angle (CCW/x)

    catalName = "catalog.dat"
    objRoot = "./"
    inFolder = "./"
    monsta = "monsta"
    config = "./"

    def __init__(
        self,
        name,
        inFolder=None,
        outFolder=None,
        config="./",
        automatic=True,
        force_new=False,
    ):

        self.config = config
        self.name = name

        self.widgets = {}

        if outFolder is None:
            outFolder = "./"

        outFolder += "Outputs_" + name + "/"

        createDir(outFolder)

        logFile = outFolder + self.name + "_model_log.csv"

        set_new_uuid = True

        if not force_new:
            try:
                if exists(logFile):
                    with open(logFile, "r") as f:
                        line = f.readline()

                    if line.strip("#").strip()[:4] == "uuid":
                        old_uuid = line.strip("#").split(":")[1].strip()
                        if os.path.isdir(outFolder + self.name + "_" + old_uuid):

                            self.uuid = old_uuid
                            self.params = get_obj_params(open_log_df(logFile))
                            set_new_uuid = False
            except:
                pass

        if set_new_uuid:
            self.uuid = str(uuid.uuid4()).split("-")[-1]
            self.params = {}

        objRoot = outFolder + name + "_" + self.uuid
        createDir(objRoot)
        print('Creating output folder: ',objRoot)
        
        self.objRoot = objRoot + "/"

        if inFolder is not None:
            self.inFolder = inFolder + "/"

        if automatic:
            try:
                self.SExtract()
            except:
                print("Error: Could not run Source Extractor on the file")
                fits_file = self.inFolder + "{}/{}j.fits".format(name, name)
                if not os.path.exists(fits_file):
                    print("Couldn't find " + fits_file)
                return

        hdu_list = fits.open(self.inFolder + "{}/{}j.fits".format(name, name))
        image_data = hdu_list[0].data
        # w = wcs.WCS(hdu_list[0].header)
        self.x_max, self.y_max = image_data.shape

        if automatic:
            self.backSextract()

#            self.r_max = int(
#                min([self.x0, self.x_max - self.x0, self.y0, self.y_max - self.y0])
#            )

            xx = min([self.x0, self.x_max - self.x0])
            yy = min([self.y0, self.y_max - self.y0])
            self.r_max = int(np.sqrt(xx*xx + yy*yy)               
            )

    def tv_resid(self, model=0, ax=None, options="", additions=""):
        root = self.objRoot
        suffix = ".%03d" % model
        fits_file = root + "/resid" + suffix
        return self.tv(fits_file=fits_file, ax=ax, options=options, additions=additions)

    def tv_model(self, model=0, ax=None, options="", additions=""):
        root = self.objRoot
        suffix = ".%03d" % model
        fits_file = root + "/model" + suffix
        return self.tv(fits_file=fits_file, ax=ax, options=options, additions=additions)

    def tv_mask(self, mask=None, ax=None, options="", additions=""):
        root = self.objRoot

        if mask is None:
            mask_name = self.config + "/common.mask"
        else:
            suffix = ".%03d" % mask
            mask_name = root + "/mask" + suffix

        return self.tv(fits_file=mask_name, ax=ax, options=options, additions=additions)

    def tv(self, fits_file=None, ax=None, options="", additions=""):

        if fits_file is None:
            fits_file = "{}j.fits".format(self.name)

        root = self.objRoot
        jpg_name = root + "tv.jpg"

        cwd = os.getcwd()
        os.chdir(self.inFolder + "/{}".format(self.name))

        ## Monsta script
        script = (
            """
        rd 1 '"""
            + fits_file
            + """'
        """
            + additions
            + """
        tv 1 """
            + options
            + """ JPEG=tv.jpg
        q
        
        """
        )

        self.run_monsta(script, "./" + "tv.pro", "./" + "tv.log")

        xcmd("cp ./tv.jpg " + os.path.join(cwd, jpg_name), verbose=False)
        os.chdir(cwd)

        return self.plot_jpg(jpg_name, ax=ax)

    def SExtract(self):

        name = self.name
        root = self.objRoot
        config = self.config

        catalName = root + self.catalName
        segmentation = root + "segmentation.fits"

        sex_config = config + "sextractor/wfc3j_sex.config"
        PARAMETERS_NAME = config + "sextractor/sbf.param"
        FILTER_NAME = config + "sextractor/gauss_2.0_5x5.conv"
        STARNNW_NAME = config + "sextractor/default.nnw"

        cmd = (
            "sex -c "
            + sex_config
            + " "
            + self.inFolder
            + "{}/{}j.fits".format(name, name)
            + " -CHECKIMAGE_TYPE SEGMENTATION -CHECKIMAGE_NAME "
            + segmentation
            + " -CATALOG_NAME "
            + catalName
            + " -PARAMETERS_NAME "
            + PARAMETERS_NAME
            + " -FILTER_NAME "
            + FILTER_NAME
            + " -STARNNW_NAME "
            + STARNNW_NAME
        )

        # Append redirection for logging
        log_file = root + "source_extractor.log"
        cmd_with_logging = cmd + f" > {log_file} 2>&1"


        run_command(cmd.split(" "))



        col_names = self.getColName(catalName)

        df = pd.read_csv(
            catalName,
            delimiter=r"\s+",
            skiprows=len(col_names),
            header=None,
            names=col_names[:18],
            usecols=range(18),
        )

        self.x0 = df.loc[0].X_IMAGE
        self.y0 = df.loc[0].Y_IMAGE
        A = df.loc[0].A_IMAGE
        B = df.loc[0].B_IMAGE
        R = df.loc[0].KRON_RADIUS
        self.angle = df.loc[0].THETA_IMAGE
        self.a = A * R
        self.b = B * R
        self.R = R
        self.name = name

    def inputMaks(self, maskName, mask=None):

        root = self.objRoot
        if mask is None:
            outMask = "composit.mask"
        else:
            outMask = "mask" + ".%03d" % mask

        cwd = os.getcwd()
        os.chdir(root)

        xcmd("cp {} ./common.mask".format(self.config + "/common.mask"), verbose=False)

        script = """
        rd 1 common.mask
        """

        if maskName is not None:
            if os.path.isfile(maskName):
                xcmd("cp {} ./tmp.mask".format(maskName), verbose=False)
                script += """
                rd 2 tmp.mask
                mi 1 2
                """
        script += (
            """
        wd 1 """
            + outMask
            + """ 
        q
        
        """
        )
        # print(root+'obj'+suffix+'.pro', root+'obj'+suffix+'.log')

        self.run_monsta(script, root + "obj_inMask.pro", root + "obj_inMask.log")

        os.chdir(cwd)

        return os.path.join(root, outMask)

    def addMasks(self, maskList=None, mask=None):

        root = self.objRoot
        if mask is None:
            outMask = "composit.mask"
        else:
            outMask = "mask" + ".%03d" % mask

        cwd = os.getcwd()
        os.chdir(root)

        xcmd("cp {} ./common.mask".format(self.config + "/common.mask"), verbose=False)

        script = """
        rd 1 common.mask
        """

        if maskList is not None:

            for m in maskList:
                suffix = ".%03d" % m
                inMask = "./mask" + suffix
                if os.path.isfile(inMask):
                    script += (
                        """
                    rd 2 """
                        + inMask
                        + """
                    mi 1 2
                    """
                    )
        script += (
            """
        wd 1 """
            + outMask
            + """ 
        q
        
        """
        )
        # print(root+'obj'+suffix+'.pro', root+'obj'+suffix+'.log')

        self.run_monsta(
            script, root + "obj" + suffix + ".pro", root + "obj" + suffix + ".log"
        )

        os.chdir(cwd)

        return os.path.join(root, outMask)

    def outerR(self, c_kron):
        return min(int(c_kron * np.sqrt(self.a * self.b)), self.r_max)

    def maskOpen(self, mask=None, maskFile=None):
        root = self.objRoot

        cwd = os.getcwd()
        os.chdir(root)

        if maskFile is None:
            if mask is None:
                inMask = "common.mask"
                xcmd(
                    "cp {} ./common.mask".format(self.config + "/common.mask"),
                    verbose=False,
                )
            else:
                suffix = ".%03d" % mask
                inMask = "mask" + suffix
        else:
            xcmd("cp {} ./tmp.mask".format(maskFile), verbose=False)
            inMask = "tmp.mask"

        ## Monsta script
        script = (
            """
        rd 1 """
            + inMask
            + """
        wd 1 """
            + inMask
            + ".fits"
            + """ 
        q

        """
        )

        run_monsta(script, "monsta.pro", "monsta.log")
        xcmd("rm monsta.log; rm monsta.pro", False)

        image, header = imOpen(inMask + ".fits")
        xcmd("rm " + inMask + ".fits", False)

        os.chdir(cwd)

        return image, header

    def elliprof(
        self,
        inner_r=5,
        outer_r=200,
        sky=None,
        cosnx="",
        k=None,
        nr=40,
        niter=10,
        model=0,
        mask=None,
        options="",
        use_common=False,
        model_mask=None,
        monsta_silent=False,
    ):

        root = self.objRoot
        suffix = ".%03d" % model
        name = self.name

        cwd = os.getcwd()
        os.chdir(root)

        if sky is None:
            sky = self.sky_med

        if mask is None:
            xcmd(
                "cp {} ./common.mask".format(self.config + "/common.mask"),
                verbose=False,
            )
            maskName = "common.mask"
            monsta_masking = """
        cop 3 1 
        """
        elif model_mask is None:
            maskName = "mask" + ".%03d" % mask
            monsta_masking = """
        cop 3 1 
        """
        else:
            maskName = "mask" + ".%03d" % mask
            model_mask = "model" + ".%03d" % model_mask
            monsta_masking = (
                """
        cop 6 2
        mc 6 0
        ac 6 1
        si 6 2
        rd 7 """
                + model_mask
                + """
        sc 7 """
                + str(sky)
                + """   ! aky subtraction
        mi 7 6
        cop 3 1 
        ai 3 7 
        """
            )

        if cosnx == "":
            kosnx = ""
        else:
            if k is None:
                kosnx = cosnx + "=0"
            else:
                kosnx = cosnx + "=" + str(k)

        residName = "resid" + suffix
        modelName = "model" + suffix
        ellipseFile = "elliprof" + suffix
        objName = self.name + suffix

        elliprof_cmd = (
            "elliprof 3  model rmstar x0=" + str(self.x0) + " y0=" + str(self.y0)
        )
        elliprof_cmd += (
            " r0="
            + str(inner_r)
            + " r1="
            + str(outer_r)
            + " nr="
            + str(nr)
            + " niter="
            + str(niter)
            + " "
            + kosnx
        )
        elliprof_cmd += " " + options

        objFits = self.inFolder + "{}/{}j.fits".format(name, name)
        xcmd("cp {} ./{}j.fits".format(objFits, name), verbose=False)
        objFits = "{}j.fits".format(name)

        ## Monsta script
        script = (
            """
        string name '"""
            + self.name
            + """'
        rd 1 '"""
            + objFits
            + """'
        sc 1 """
            + str(sky)
            + """                            ! sky subtraction
        rd 2 """
            + maskName
            + """
        mi 1 2
        tv 1 sqrt JPEG="""
            + objName
            + """.jpg

        """
        )

        script += monsta_masking

        script += elliprof_cmd
        script += (
            """
        print elliprof file="""
            + ellipseFile
            + """
        cop 4 1                               ! object
        si 4 3                                ! object - model
        ac 3 """
            + str(sky)
            + """                  
        !mi 3 2 
        mi 4 2                                ! multiply by mask
        wd 3 """
            + modelName
            + """
        wd 4 """
            + residName
            + """
        tv 4 JPEG="""
            + residName
            + """.jpg
        tv 3 JPEG="""
            + modelName
            + """.jpg
        q
        
        """
        )

        Monsta_pro = root + "monsta" + suffix + ".pro"
        Monsta_log = root + "monsta" + suffix + ".log"

        monsta_output = self.run_monsta(
            script, Monsta_pro, Monsta_log, silent=monsta_silent
        )
        os.chdir(cwd)

        return monsta_output

    def objSourceExtract(
        self, model=0, smooth=None, minArea=10, thresh=2, mask=None, renuc=1
    ):

        root = self.objRoot
        suffix = ".%03d" % model

        if mask is None:
            suffix_mask = ".%03d" % model
        else:
            suffix_mask = ".%03d" % mask

        cwd = os.getcwd()
        os.chdir(root)

        residName = "resid" + suffix
        modelName = "model" + suffix
        segment = "objCheck" + suffix + ".segment"
        objName = "objCheck" + suffix
        objCatal = "objCatal" + suffix
        maskName = "mask" + suffix_mask
        model_mask = "mask" + ".%03d" % model
        tmp = "tmp"

        name = self.name

        objFits = self.inFolder + "{}/{}j.fits".format(name, name)
        xcmd("cp {} ./{}j.fits".format(objFits, name), verbose=False)
        objFits = "{}j.fits".format(name)

        script = (
            """
        rd 1 '"""
            + objFits
            + """'
        rd 2 """
            + model_mask
            + """
        rd 3 """
            + modelName
            + """
        si 1 3
        mi 1 2
        wd 1 '"""
            + residName
            + """'
        q
        """
        )
        self.run_monsta(script, root + "obj.pro", root + "obj.log")

        # print(root+'obj.pro')

        if smooth is not None:
            script = (
                """
            rd 1 """
                + residName
                + """
            smooth 1 fw="""
                + str(smooth)
                + """
            wd 1 """
                + tmp
                + """
            q
            
            """
            )
            residName = tmp
            self.run_monsta(script, root + "obj.pro", root + "obj.log")

        variance = modelName
        if renuc is not None and renuc != 1:
            variance = root + "/model" + suffix + "_renuc_" + str(renuc)
            script = (
                """
            rd 1 """
                + modelName
                + """
            mc 1 """
                + str(renuc)
                + """
            wd 1 """
                + variance
                + """
            q
            
            """
            )

            self.run_monsta(script, root + "obj.pro", root + "obj.log")

        config = self.config

        sex_config = config + "sextractor/wfc3j.inpar"
        PARAMETERS_NAME = config + "sextractor/sbf.param"
        FILTER_NAME = config + "sextractor/gauss_2.0_5x5.conv"
        STARNNW_NAME = config + "sextractor/default.nnw"

        # Construct command for SExtractor
        sex_cmd = (
            f"sex {residName} -c {sex_config} "
            f"-CHECKIMAGE_NAME {segment} "
            f"-CATALOG_NAME {objCatal} "
            f"-DETECT_MINAREA {minArea} "
            f"-DETECT_THRESH {thresh} "
            f"-ANALYSIS_THRESH {thresh} "
            f'-CHECKIMAGE_TYPE "SEGMENTATION" '
            f"-PARAMETERS_NAME {PARAMETERS_NAME} "
            f"-FILTER_NAME {FILTER_NAME} "
            f"-STARNNW_NAME {STARNNW_NAME}"
        )

        if renuc is not None:
            sex_cmd += (
                f" -WEIGHT_IMAGE {variance} "
                f"-WEIGHT_TYPE MAP_VAR"
            )

        run_command(sex_cmd.split(" "))
        seg2mask(segment, objName)

        xcmd("cp {} ./common.mask".format(self.config + "/common.mask"), verbose=False)

        ## Monsta script
        script = (
            """
        rd 1 """
            + objName
            + """
        rd 5 common.mask
        mi 1 5
        wd 1 """
            + maskName
            + """ bitmap
        tv 1 JPEG="""
            + maskName
            + """.jpg
        q
        
        """
        )
        # print(root+'obj'+suffix+'.pro', root+'obj'+suffix+'.log')

        monsta_output = self.run_monsta(
            script, root + "obj" + suffix + ".pro", root + "obj" + suffix + ".log"
        )

        os.chdir(cwd)
        return monsta_output

    def naive_Sextract(self, minArea=10, thresh=2, mask=None, smooth=None):

        name = self.name
        root = self.objRoot

        cwd = os.getcwd()
        os.chdir(root)

        xcmd("cp {} ./common.mask".format(self.config + "/common.mask"), verbose=False)
        objFits = self.inFolder + "{}/{}j.fits".format(name, name)
        xcmd("cp {} ./{}j.fits".format(objFits, name), verbose=False)
        fits_name = "{}j.fits".format(name)

        odj_common = "tmp"

        if smooth is not None:
            script = (
                """
            rd 1 {}
            smooth 1 fw={}
            wd 1 {}
            q
            """.format(fits_name, smooth, odj_common)
            )
            fits_name = odj_common
            self.run_monsta(script, root + "obj.pro", root + "obj.log")

        model = 0
        suffix_mask = ".%03d" % (mask if mask is not None else model)
        maskName = root + "/mask" + suffix_mask

        script = (
            """
        rd 1 {}
        rd 2 common.mask
        mi 1 2
        wd 1 {}
        q
        """.format(fits_name, odj_common)
        )
        self.run_monsta(script, root + "obj.pro", root + "obj.log")

        config = self.config
        sex_config = config + "sextractor/wfc3j_sex.config"
        PARAMETERS_NAME = config + "sextractor/sbf.param"
        FILTER_NAME = config + "sextractor/gauss_2.0_5x5.conv"
        STARNNW_NAME = config + "sextractor/default.nnw"

        cmd = (
            "sex -c {} {} -BACK_SIZE 500 -DETECT_MINAREA {} -DETECT_THRESH {} "
            '-CHECKIMAGE_TYPE "SEGMENTATION" -CHECKIMAGE_NAME {} '
            "-CATALOG_NAME {} "
            "-PARAMETERS_NAME {} "
            "-FILTER_NAME {} "
            "-STARNNW_NAME {}"
        ).format(
            sex_config, odj_common, minArea, thresh, maskName, root + "/naive_sextract_wfc3j.cat",
            PARAMETERS_NAME, FILTER_NAME, STARNNW_NAME
        )

        run_command(cmd.split(" "))


        im, header = imOpen(maskName)
        x0 = int(np.round(self.x0))
        y0 = int(np.round(self.y0))

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(11, 4))

        im, header = imOpen(maskName)
        ax1.imshow(np.flipud(im))

        mask2 = seg2mask(maskName, maskName, seg_num=im[x0, y0])
        im, _ = imOpen(odj_common)

        os.chdir(cwd)

        return fig, ax1, ax2, ax3, ax4

    def backSextract(self, thresh=0.03):

        name = self.name
        root = self.objRoot
        config = self.config
        fits_name = self.inFolder + "{}/{}j.fits".format(name, name)
        odj_common = root + "/tmp"
        segmentation = root + "back_mask.fits"

        sex_config = config + "sextractor/wfc3j_sex.config"
        PARAMETERS_NAME = config + "sextractor/sbf.param"
        FILTER_NAME = config + "sextractor/gauss_2.0_5x5.conv"
        STARNNW_NAME = config + "sextractor/default.nnw"

        # Run MONSTA
        script = (
            f"""
            rd 1 {fits_name}
            rd 2 {self.config}/common.mask
            mi 1 2
            wd 1 {odj_common}
            q
            """
        )
        self.run_monsta(script, root + "obj.pro", root + "obj.log")

        # Construct command for SExtractor
        cmd = (
            f"sex -c {sex_config} {odj_common} "
            f"-CATALOG_NAME {root}/background_wfc3j.cat "
            f"-BACK_SIZE 500 -DETECT_MINAREA 4 -DETECT_THRESH {thresh} "
            f'-CHECKIMAGE_TYPE "SEGMENTATION" -CHECKIMAGE_NAME {segmentation} '
            f"-PARAMETERS_NAME {PARAMETERS_NAME} "
            f"-FILTER_NAME {FILTER_NAME} "
            f"-STARNNW_NAME {STARNNW_NAME}"
        )

        run_command(cmd.split(" "))

        mask2 = seg2mask(segmentation, segmentation)
        im, _ = imOpen(odj_common)

        masked_image = im * mask2
        a = masked_image
        a = a[(a != 0)]
        std = np.std(a)
        median = np.median(a)
        a = a[((a > median - 3.0 * std) & (a < median + 3.0 * std))]

        self.sky_med = np.median(a)
        self.sky_ave = np.mean(a)
        self.sky_std = np.std(a)

        self.masked_image = masked_image
        self.back_pixels = a

        return im, mask2

    def run_monsta(self, script, Monsta_pro, Monsta_log, silent=False):

        with open(Monsta_pro, "w") as f:
            f.write(script)

        cmd = self.monsta + " " + Monsta_pro
        xcmd(cmd + " > " + Monsta_log, verbose=False)

        with open(Monsta_log) as f:
            text = f.read()
        Tsplit = text.upper().split()
        if "ERROR" in Tsplit or "SEGMENTATION FAULT" in Tsplit:
            if not silent:
                print("===== MONSTA =====")
                for i, line in enumerate(script.split("\n")):
                    print(f"{i+1:>4}{line}")
                print("===================")
                print(text)
                return text
            else:
                return "[Warning] MONSTA NOT OK !"
        else:
            return "OK"

    def getColName(self, catalName):
        with open(catalName, "r") as f:

            lines = f.readlines()

        col_names = []
        i = 0
        while lines[i].split()[0] == "#":
            col_names.append(lines[i].split()[2])
            i += 1

        return col_names

    def set_center(self, x0, y0):
        self.x0 = x0
        self.y0 = y0

    def get_center(self):
        return self.x0, self.y0

    def plot_jpg(self, jpg_name, ax=None):

        img = mpimg.imread(jpg_name)
        x_max, y_max, _ = img.shape

        if ax is None:
            plt.figure(figsize=(10, 10))
            plt.subplot(111)
            ax = plt.gca()

        ax.set_xlim([0, self.x_max])
        ax.set_ylim([0, self.y_max])

        imgplot = ax.imshow(np.flipud(img))

        return ax

    def plot_mask(self, mask=0, ax=None):

        root = self.objRoot
        suffix = ".%03d" % mask

        jpg_name = root + "/mask" + suffix + ".jpg"

        return self.plot_jpg(jpg_name, ax=ax)

    def plot_resid(self, model=0, ax=None):

        root = self.objRoot
        suffix = ".%03d" % model

        jpg_name = root + "/resid" + suffix + ".jpg"

        return self.plot_jpg(jpg_name, ax=ax)

    def plot_object(self, model=0, ax=None):

        root = self.objRoot
        suffix = ".%03d" % model

        jpg_name = root + "/" + self.name + suffix + ".jpg"

        return self.plot_jpg(jpg_name, ax=ax)

    def list_ellipses(self, model=0):

        root = self.objRoot
        suffix = ".%03d" % model

        ellipseFile = root + "/elliprof" + suffix
        df = pd.read_csv(ellipseFile, delimiter=r"\s+", skiprows=7)
        df = df.apply(pd.to_numeric, errors="coerce")

        return list_Ell(df)

    def plot_ellipse(self, model=0, ax=None, **kwargs):

        root = self.objRoot
        suffix = ".%03d" % model

        ellipseFile = root + "/elliprof" + suffix
        df = pd.read_csv(ellipseFile, delimiter=r"\s+", skiprows=7)
        df = df.apply(pd.to_numeric, errors="coerce")

        if ax is None:
            plt.figure(figsize=(10, 10))
            plt.subplot(111)
            ax = plt.gca()
            ax.set_xlim([0, self.x_max])
            ax.set_ylim([0, self.y_max])

        for i in range(len(df)):
            plot_E(df.iloc[i], ax=ax, **kwargs)

        return ax

    def plot_background(self):

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11, 3), gridspec_kw={'wspace': 0.4})

        # ax1 = axes[0][0]
        # ax2 = axes[0][1]
        # ax3 = axes[1][0]
        # ax4 = axes[1][1]  # Reference to the axes you want to be blank

        # Turn off the ax4 plot
        # ax4.axis("off")  # Makes the entire subplot blank

        ## objects are masked, display background pixels
        ax1 = plot_2darray(self.masked_image, ax=ax1)
        ax1.set_title("Back. Mask", fontsize=14)
        ax1.set_xlabel("X [pixel]", fontsize=12)
        ax1.set_ylabel("Y [pixel]", fontsize=12)

        print("Background Median: %.0f" % self.sky_med)
        print("Background Mean: %.0f" % self.sky_ave)
        print("Background Stdev: %.0f" % self.sky_std)

        ## Histogram of the potential background pixel values
        ax2.hist(
            self.back_pixels,
            bins=np.linspace(
                self.sky_med - 3 * self.sky_std, self.sky_med + 3 * self.sky_std, 20
            ),
            density=True,
            color="g",
            alpha=0.7,
        )
        ax2.set_xlabel("pixel value", fontsize=12)
        ax2.set_ylabel("frequency", fontsize=12)
        ax2.set_title("Background Histogram", fontsize=14)

        self.tv(options="log", ax=ax3)
        ax3.set_title(self.name, fontsize=14)

        return fig, (ax1, ax2, ax3)

    #########################################################
    def basic_elliprof(self, pngName=None):

        main_key = "basic_elliprof"

        r0 = self.params[main_key]["r0"] = self.widgets[main_key + "_r0"].value
        c_kron = self.params[main_key]["c_kron"] = self.widgets[
            main_key + "_ckron"
        ].value
        r1 = self.outerR(c_kron)
        k = self.params[main_key]["k_ellipse"] = self.widgets[main_key + "_k"].value
        nr = int(np.round((r1 - r0) / k))
        sky_factor = self.params[main_key]["sky_factor"] = self.widgets[
            main_key + "_skyfactor"
        ].value

        sky = int(sky_factor * self.sky_med)
        options = self.params[main_key]["option"] = self.widgets[
            main_key + "_option"
        ].value

        # input mask. Usually mask = 1 or any value chosen for the initial mask from the previous cell
        # since we have not specify the model number, the generated model takes a value of `0`
        msg = self.elliprof(r0, r1, nr=nr, sky=sky, niter=10, options=options, mask=1)

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11, 5))

        ## Calculating the number of crossing ellipses, the generated model = 0, from previous linen_cross = Xellipses(obj.list_ellipses(model=0))
        self.tv(options="log", ax=ax1)
        ax1.set_title(self.name, fontsize=14)
        self.plot_ellipse(
            model=0, ax=ax1, alpha=0.5, linewidth=1, edgecolor="r", facecolor="none"
        )

        n_cross = Xellipses(self.list_ellipses(model=0))

        print("N_cross: %d" % n_cross)  # No. of crossing ellipses
        print("r0: %d" % r0)
        print("r1: %d" % r1)
        print("nr: %d" % nr)
        print("sky: %d" % sky)

        self.tv_mask(mask=1, ax=ax2)
        ax2.set_title("Mask 1", fontsize=14)

        self.tv_resid(model=0, ax=ax3, options="sqrt")
        ax3.set_title("Residual", fontsize=14)

        if pngName is None:
            pngName = self.objRoot + "/" + self.name + "_basic_model.png"
        else:
            pngName = self.objRoot + "/" + pngName

        plt.savefig(pngName)
        print("fig. name: ", pngName)

        fig.tight_layout(pad=0)
        try: 
            fig.canvas.layout.width = '1100px'  # Set width to match figsize
            fig.canvas.layout.height = '500px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass

        return (ax1, ax2)

    #########################################################
    def slider_back_threshold(self):

        main_key = "backSextract"

        s = self.add_widget(
            main_key,
            "threshold",
            "backSextract_thresh",
            params={
                "default": 0.03,
                "min": 0.01,
                "max": 0.16,
                "step": 0.01,
                "description": "Threshold",
            },
        )

        return s

    #########################################################
    def plot_back_mask(self, pngName=None):

        thresh = self.params["backSextract"]["threshold"] = self.widgets[
            "backSextract_thresh"
        ].value

        self.backSextract(thresh=thresh)
        fig, [ax1, ax2, ax3] = self.plot_background()

        if pngName is None:
            pngName = self.objRoot + self.name + "_initial_back.png"
        else:
            pngName = self.objRoot + pngName

        plt.savefig(pngName)
        print("fig. name: ", pngName)

        # fig.tight_layout(pad=4)
        try: 
            fig.canvas.layout.width = '1100px'  # Set width to match figsize
            fig.canvas.layout.height = '300px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass

        return (ax1, ax2, ax3)

    #########################################################
    def add_widget(
        self, main_key, second_key, widget_name, params={}, widget_type="slider"
    ):

        if not main_key in self.params:
            self.params[main_key] = {}

        if not second_key in self.params[main_key]:
            self.params[main_key][second_key] = params["default"]

        if widget_name in self.widgets:
            self.params[main_key][second_key] = self.widgets[widget_name].value

        value = self.params[main_key][second_key]

        try:
            if widget_type == "slider":
                my_widget = widgets.FloatSlider(
                    value=value,
                    min=params["min"],
                    max=params["max"],
                    step=params["step"],
                    description=params["description"],
                )
            elif widget_type == "dropdown":
                my_widget = widgets.Dropdown(
                    value=value,
                    options=params["options"],
                    description=params["description"],
                )
            else:
                return None
        except:
            return None

        self.widgets[widget_name] = my_widget

        return [my_widget]

    #########################################################
    def slider_naive_extractor(self):

        main_key = "naiveSextract"

        s = self.add_widget(
            main_key,
            "minarea",
            "naive_minarea",
            params={
                "default": 200,
                "min": 5,
                "max": 1000,
                "step": 1,
                "description": "Min_Area",
            },
        )

        s += self.add_widget(
            main_key,
            "threshold",
            "naive_thresh",
            params={
                "default": 3,
                "min": 0.5,
                "max": 5,
                "step": 0.1,
                "description": "Threshold",
            },
        )

        s += self.add_widget(
            main_key,
            "smooth",
            "naive_smooth",
            params={
                "default": 5,
                "min": 1,
                "max": 10,
                "step": 0.5,
                "description": "Smooth",
            },
        )

        return s

    #########################################################
    def plot_naives_source_extract(self, pngName=None):

        main_key = "naiveSextract"

        minarea = self.params[main_key]["minarea"] = self.widgets["naive_minarea"].value
        threshold = self.params[main_key]["threshold"] = self.widgets[
            "naive_thresh"
        ].value
        smooth = self.params[main_key]["smooth"] = self.widgets["naive_smooth"].value

        fig, ax1, ax2, ax3, ax4 = self.naive_Sextract(
            minArea=minarea, thresh=threshold, mask=0, smooth=smooth
        )
        ax1.set_title("SE segmentation", fontsize=14)

        self.addMasks(maskList=[0], mask=1)

        ## importing Dmask and add it to the initial mask we find using
        ## a crude SExtractor run
        Dmask = self.inFolder + "{}/{}j.dmask".format(self.name, self.name)
        if os.path.exists(Dmask):
            self.inputMaks(Dmask, mask=0)
            self.addMasks(maskList=[0, 1], mask=1)

            im, h = self.maskOpen(mask=0)
            ax3.imshow(np.flipud(im))
            ax3.set_title("dmask", fontsize=14)

        else:
            print(Dmask + " doesn't exist.")

        im, h = self.maskOpen(mask=1)
        ax2.imshow(np.flipud(im))
        ax2.set_title("Mask 1", fontsize=14)

        self.tv(options="log", ax=ax4)
        ax4.set_title(self.name, fontsize=14)

        if pngName is None:
            pngName = self.objRoot + self.name + "_initial_mask.png"
        else:
            pngName = self.objRoot + pngName

        plt.savefig(pngName)
#        print("fig. name: ", pngName)

        fig.tight_layout(pad=0)
        try: 
            fig.canvas.layout.width = '1100px'  # Set width to match figsize
            fig.canvas.layout.height = '400px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass

        return fig, ax1, ax2, ax3, ax4

    #########################################################
    def basic_elliprof_widget(self):

        main_key = "basic_elliprof"

        s = self.add_widget(
            main_key,
            "r0",
            main_key + "_r0",
            params={
                "default": 9,
                "min": 3,
                "max": 200,
                "step": 1,
                "description": "r0 [pixel]",
            },
        )

        s += self.add_widget(
            main_key,
            "c_kron",
            main_key + "_ckron",
            params={
                "default": 3.5,
                "min": 0.5,
                "max": 7,
                "step": 0.1,
                "description": "Kron_factor",
            },
        )

        s += self.add_widget(
            main_key,
            "sky_factor",
            main_key + "_skyfactor",
            params={
                "default": 0.9,
                "min": 0.1,
                "max": 1.2,
                "step": 0.05,
                "description": "Sky_factor",
            },
        )

        s += self.add_widget(
            main_key,
            "k_ellipse",
            main_key + "_k",
            params={"default": 15, "min": 5, "max": 50, "step": 1, "description": "k"},
        )

        s += self.add_widget(
            main_key,
            "option",
            main_key + "_option",
            params={
                "options": [
                    "None",
                    "COS3X=0 (none)",
                    "COS3X=1 (median)",
                    "COS3X=2 (each annulus)",
                    "COS4X=0 (none)",
                    "COS4X=1 (median)",
                    "COS4X=2 (each annulus)",
                    "COS3X=-1 (median cos(6x) model)",
                    "COS3X=-2 (each cos(6x) model)",
                ],
                "default": "None",
                "description": "Higher-order fits",
            },
            widget_type="dropdown",
        )

        return s

    #########################################################

    #########################################################
    def second_elliprof_widget(self):

        main_key = "second_elliprof"
        basic_key = "basic_elliprof"

        s1 = self.add_widget(
            main_key,
            "r0",
            main_key + "_r0",
            params={
                "default": self.params[basic_key]["r0"],
                "min": 3,
                "max": 200,
                "step": 1,
                "description": "r0 (pix)",
            },
        )

        s1 += self.add_widget(
            main_key,
            "c_kron",
            main_key + "_ckron",
            params={
                "default": self.params[basic_key]["c_kron"],
                "min": 0.5,
                "max": 7,
                "step": 0.1,
                "description": "Kron factor",
            },
        )

        s1 += self.add_widget(
            main_key,
            "sky_factor",
            main_key + "_skyfactor",
            params={
                "default": self.params[basic_key]["sky_factor"],
                "min": 0.1,
                "max": 1.2,
                "step": 0.01,
                "description": "Sky factor",
            },
        )

        s1 += self.add_widget(
            main_key,
            "k_ellipse",
            main_key + "_k",
            params={
                "default": self.params[basic_key]["k_ellipse"],
                "min": 5,
                "max": 50,
                "step": 1,
                "description": "k ellipse",
            },
        )

        s1 += self.add_widget(
            main_key,
            "option",
            main_key + "_option",
            params={
                "options": [
                    "None",
                    "COS3X=0 (none)",
                    "COS3X=1 (median)",
                    "COS3X=2 (each annulus)",
                    "COS4X=0 (none)",
                    "COS4X=1 (median)",
                    "COS4X=2 (each annulus)",
                    "COS3X=-1 (median cos(6x) model)",
                    "COS3X=-2 (each cos(6x) model)",
                ],
                "default": "None",
                "description": "Higher-order fits",
            },
            widget_type="dropdown",
        )

        s2 = self.add_widget(
            main_key,
            "minarea",
            main_key + "_minarea",
            params={
                "default": 300,
                "min": 5,
                "max": 1000,
                "step": 1,
                "description": "Min Area",
            },
        )

        s2 += self.add_widget(
            main_key,
            "threshold",
            main_key + "_thresh",
            params={
                "default": 3,
                "min": 0.5,
                "max": 5,
                "step": 0.1,
                "description": "Threshold",
            },
        )

        s2 += self.add_widget(
            main_key,
            "smooth",
            main_key + "_smooth",
            params={
                "default": 5,
                "min": 1,
                "max": 10,
                "step": 0.5,
                "description": "Smooth",
            },
        )

        s2 += self.add_widget(
            main_key,
            "renuc",
            main_key + "_renuc",
            params={
                "default": 2,
                "min": 1,
                "max": 10,
                "step": 0.5,
                "description": "Renuc",
            },
        )

        return s1, s2

    #########################################################
    def second_elliprof(self, pngName=None):

        main_key = "second_elliprof"

        r0 = self.params[main_key]["r0"] = self.widgets[main_key + "_r0"].value
        c_kron = self.params[main_key]["c_kron"] = self.widgets[
            main_key + "_ckron"
        ].value
        r1 = self.outerR(c_kron)
        k = self.params[main_key]["k_ellipse"] = self.widgets[main_key + "_k"].value
        nr = int(np.round((r1 - r0) / k))
        sky_factor = self.params[main_key]["sky_factor"] = self.widgets[
            main_key + "_skyfactor"
        ].value

        sky = int(sky_factor * self.sky_med)
        options = self.params[main_key]["option"] = self.widgets[
            main_key + "_option"
        ].value

        minarea = self.params[main_key]["minarea"] = self.widgets[
            main_key + "_minarea"
        ].value
        threshold = self.params[main_key]["threshold"] = self.widgets[
            main_key + "_thresh"
        ].value
        smooth = self.params[main_key]["smooth"] = self.widgets[
            main_key + "_smooth"
        ].value
        renuc = self.params[main_key]["renuc"] = self.widgets[main_key + "_renuc"].value

        ## using mask=1  --> primary mask
        ## generate model = 0
        ## uses model_mask for the masked regions
        self.elliprof(
            r0,
            r1,
            nr=nr,
            sky=self.sky_med * sky_factor,
            niter=50,
            mask=1,
            model_mask=0,
            options=options,
        )

        # using residuals of model 0 --> mask 2
        self.objSourceExtract(
            model=0,
            smooth=smooth,
            minArea=minarea,
            thresh=threshold,
            mask=2,
            renuc=renuc,
        )

        # plotting model 0

        fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(11, 5))

        self.tv_resid(model=0, ax=ax0, options="sqrt")
        Ell = ((self.x0, self.y0), 1.0 * self.a, 1.0 * self.b, self.angle)
        e = patches.Ellipse(
            Ell[0],
            width=2 * Ell[1],
            height=2 * Ell[2],
            angle=Ell[3],
            alpha=0.5,
            linewidth=1,
            edgecolor="r",
            facecolor="none",
        )
        ax0.add_patch(e)
        ax0.set_title("Residual")

        self.tv_mask(mask=2, ax=ax1)
        self.plot_ellipse(
            model=0,
            ax=ax1,
            alpha=0.5,
            linewidth=1,
            edgecolor="r",
            facecolor="none",
        )

        self.tv(ax=ax2, options="sqrt")
        ax2.set_title(self.name, fontsize=14)
        # self.tv_model(model=0, ax=ax[1, 1], options="sqrt")
        # ax[1, 1].set_title("Model")

        pngName = self.objRoot + "/" + self.name + "_initial_model.png"
        plt.savefig(pngName)
        print("fig. name: ", pngName)

        ax1.set_title("Mask 2 (additional)")

        resid = True

        # text = ax2.text(0, 0, "", va="bottom", ha="left")

        text = ax2.text(
            -0.1, -0.2,  # Coordinates outside the axes (relative to the axes)
            "", 
            va="bottom", ha="left",
            transform=ax2.transAxes  # Use axes-relative coordinates
        )

        pointer0, = ax0.plot([], [], 'r+', markersize=5)  # Red point for the pointer
        pointer1, = ax1.plot([], [], 'r+', markersize=5)  # Red point for the pointer
        pointer2, = ax2.plot([], [], 'r+', markersize=5)  # Red point for the pointer
        def on_mouse_move(event):

            tx = "x=%f, y=%f" % (
                event.xdata,
                event.ydata,
            )
            text.set_text(tx)

            if event.inaxes == ax0:
                x, y = event.xdata, event.ydata
                pointer0.set_data([], [])
                pointer1.set_data([x], [y])
                pointer2.set_data([x], [y])
                fig.canvas.draw_idle()
            if event.inaxes == ax1:
                x, y = event.xdata, event.ydata
                pointer0.set_data([x], [y])
                pointer1.set_data([], [])
                pointer2.set_data([x], [y])
                fig.canvas.draw_idle()  # Redraw the figure
            if event.inaxes == ax2:
                x, y = event.xdata, event.ydata
                pointer0.set_data([x], [y])
                pointer1.set_data([x], [y])
                pointer2.set_data([], [])
                fig.canvas.draw_idle()  # Redraw the figure

        def onclick(event):
            global resid
            if event.inaxes == ax1:
                event.inaxes.set_title("Mask 2 (additional)")
                root = self.objRoot
                segment = root + "/objCheck.000.segment"
                objName = root + "/objCheck.000"
                maskName = root + "/mask.002"

                imarray, header = imOpen(segment)
                i = int(event.xdata)
                j = int(event.ydata)

                n = imarray[j, i]
                text.set_text(str(i) + " " + str(j) + " " + str(n))
                imarray[(imarray == n)] = 0
                fits.writeto(segment, np.float32(imarray), header, overwrite=True)
                seg2mask(segment, objName)
                ## Monsta script
                script = (
                    """
                    rd 1 """
                    + objName
                    + """
                    rd 5 """
                    + self.config
                    + """/common.mask
                    mi 1 5
                    wd 1 """
                    + maskName
                    + """ bitmap
                    tv 1 JPEG="""
                    + maskName
                    + """.jpg
                    q

                    """
                )
                self.run_monsta(script, root + "monsta.pro", root + "monsta.log")
                #             self.tv_model(model=0, ax=ax[0,1], options='sqrt')
                self.tv_mask(mask=2, ax=ax1)
                fig.canvas.draw_idle()

            if event.inaxes == ax0:
                event.inaxes.set_title(resid)
                if resid:
                    self.tv(ax=ax0, options="sqrt")
                    resid = False
                else:
                    self.tv_resid(model=0, ax=ax0, options="sqrt")
                    resid = True
                fig.canvas.draw_idle()

        fig.canvas.callbacks.connect("button_press_event", onclick)
        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

        fig.tight_layout(pad=0)
        try: 
            fig.canvas.layout.width = '1100px'  # Set width to match figsize
            fig.canvas.layout.height = '500px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass

        return fig, (ax0, ax1, ax2)

    #########################################################
    def optimize_sky_factor(
        self,
        sky_factor,
        r0,
        r1,
        nr,
        options="",
        mask=1,
        model_mask=0,
        n_repeat=25,
        model=0,
        verbose=False,
    ):

        First = True

        for i in range(n_repeat):

            sky = sky_factor * self.sky_med

            if (
                self.elliprof(
                    r0,
                    r1,
                    nr=nr,
                    sky=sky,
                    niter=10,
                    mask=mask,
                    model_mask=model_mask,
                    model=model,
                    monsta_silent=True,
                )
                != "OK"
            ):
                return 0

            resid_name = self.objRoot + "resid" + ".%03d" % model
            back_mask = self.objRoot + "back_mask.fits"

            imarray, header = imOpen(resid_name)
            mskarray, header = imOpen(back_mask)

            masked_image = imarray * mskarray

            a = masked_image
            a = a[(a != 0)]
            std = np.std(a)
            mean = np.mean(a)

            a = a[((a > mean - 3.0 * std) & (a < mean + 3.0 * std))]

            median = np.median(a)
            mean = np.mean(a)
            std = np.std(a)

            sky_factor = median / self.sky_med + sky_factor

            abs_median = np.abs(median)
            if First:
                min_absmed = abs_median
                min_factor = sky_factor
                min_med = median
                First = False
            elif abs_median < min_absmed:
                min_absmed = abs_median
                min_factor = sky_factor
                min_med = median

            if i % 5 == 0 and verbose:
                print("%02d median:%.2f factor:%.4f" % (i, median, sky_factor))

        if verbose:
            print("Optimum --- median:%.2f factor:%.4f" % (min_med, min_factor))

        ## Finally generate a model for the optimum sky_factor
        self.elliprof(
            r0,
            r1,
            nr=nr,
            sky=min_factor * self.sky_med,
            niter=10,
            mask=mask,
            model_mask=model_mask,
            model=model,
        )

        return min_factor

    #########################################################
    #########################################################
    def plot_profile(
        self,
        sky_factor,
        r0,
        r1,
        nr,
        options="",
        mask=1,
        model_mask=0,
        fit_imits=[70, 90],
    ):

        # using final mask = 1 --> model 0
        self.elliprof(
            r0,
            r1,
            nr=nr,
            sky=self.sky_med * sky_factor,
            niter=10,
            mask=mask,
            model_mask=model_mask,
            options=options,
        )

        model = 0
        root = self.objRoot
        suffix = ".%03d" % model

        ellipseFile = root + "/elliprof" + suffix
        df = pd.read_csv(ellipseFile, delimiter=r"\s+", skiprows=7)
        df = df.apply(pd.to_numeric, errors="coerce")

        # fig, ax = plt.subplots(1,1, figsize=(7,6))
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        x = df.Rmaj ** 0.25
        y = 2.5 * np.log10(df.I0)
        ax.plot(x, y, ".")

        ax.set_xlabel(r"$r^{1/4}$" + " [pixel]", fontsize=16)
        ax.set_ylabel(r"surface brightness" + " [mag]", fontsize=16)

        range_0 = fit_imits[0] / 100
        range_1 = 1.0 - fit_imits[1] / 100

        maxX = np.max(x)
        minX = np.min(x)
        dx = maxX - minX
        x1 = range_0 * dx + minX
        x2 = maxX - range_1 * dx
        x0 = x[((x < x2) & (x > x1))]
        y0 = y[((x < x2) & (x > x1))]
        ax.plot(x0, y0, "ko", mfc="none")

        m, b = np.polyfit(x0, y0, 1)

        xrange = np.linspace(x1 - 0.2 * dx, maxX + 0.1 * dx, 100)
        yrange = m * xrange + b

        ax.plot(xrange, yrange, "r:")
        set_axes(ax, fontsize=14)

        ax.set_title(self.name, fontsize=14, color="maroon")
        ##################################################
        self.tv_resid(model=0, options="sqrt", ax=ax2)
        self.plot_ellipse(
            model=0, ax=ax2, alpha=0.5, linewidth=1, edgecolor="r", facecolor="none"
        )
        n_cross = Xellipses(self.list_ellipses(model=0))
        print("No. of crossing ellipses: %d" % n_cross)

        ## center, Smajor, Smainor, angle
        Ell = make_Ellipse((self.x0, self.y0), min(x0) ** 4, min(x0) ** 4, 0)
        e = patches.Ellipse(
            Ell[0],
            width=2 * Ell[1],
            height=2 * Ell[2],
            angle=Ell[3],
            alpha=0.5,
            linewidth=1,
            edgecolor="yellow",
            facecolor="none",
        )
        ax2.add_patch(e)

        Ell = make_Ellipse((self.x0, self.y0), max(x0) ** 4, max(x0) ** 4, 0)
        e = patches.Ellipse(
            Ell[0],
            width=2 * Ell[1],
            height=2 * Ell[2],
            angle=Ell[3],
            alpha=0.5,
            linewidth=1,
            edgecolor="yellow",
            facecolor="none",
        )
        ax2.add_patch(e)

        pngName = self.objRoot + self.name + "_light_profile.png"
        plt.savefig(pngName)
        print("fig. name: ", pngName)

        csv_name = self.objRoot + self.name + "_light_profile.csv"
        df.to_csv(csv_name)
        print("profile table name: ", csv_name)

        print(df.head())


        fig.tight_layout(pad=0)
        try: 
            fig.canvas.layout.width = '1000px'  # Set width to match figsize
            fig.canvas.layout.height = '400px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass

        return (ax, ax2)

    #########################################################
    def plot_back_histogram(self, sky_factor):

        resid_name = self.objRoot + "resid.000"
        back_mask = self.objRoot + "back_mask.fits"

        imarray, header = imOpen(resid_name)
        mskarray, header = imOpen(back_mask)

        masked_image = imarray * mskarray

        fits.writeto(
            self.objRoot + "tmp.fits", np.float32(masked_image), overwrite=True
        )

        ## plot_2darray(imarray)
        # tv('./tmp.fits', options='log')

        a = masked_image
        a = a[(a != 0)]
        std = np.std(a)
        mean = np.mean(a)

        a = a[((a > mean - 3.0 * std) & (a < mean + 3.0 * std))]

        median = np.median(a)
        mean = np.mean(a)
        std = np.std(a)

        print("Back Median: %.2f" % median)
        print("Back Mean: %.2f" % mean)
        print("Back Stdev: %.2f" % std)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.hist(
            a,
            bins=np.linspace(mean - 5 * std, mean + 5 * std, 10),
            density=True,
            color="g",
            alpha=0.7,
        )
        tv(self.objRoot + "tmp.fits", ax=ax2, options="")

        ax1.axvline(x=0, color="r", linestyle=":")
        ax1.set_title("input sky factor: %.3f" % sky_factor)
        ax2.set_title("background pixels")

        new_factor = median / self.sky_med + sky_factor

        pngName = self.objRoot + self.name + "_updated_back.png"
        plt.savefig(pngName)
        print("fig. name: ", pngName)

        print("\nNew potential sky factor:", "%.3f" % new_factor)
        print(
            "Note that the suggested sky factor is determined based on the histogram of \nthe background pixels in the residual image !!!"
        )

        self.params["background"] = {}
        self.params["background"]["median"] = median
        self.params["background"]["mean"] = mean
        self.params["background"]["std"] = std
        self.params["background"]["new_sky_factor"] = new_factor

        fig.tight_layout(pad=0)
        try: 
            fig.canvas.layout.width = '1000px'  # Set width to match figsize
            fig.canvas.layout.height = '400px'  # Set height to match figsize
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
        except:
            pass


        return (ax1, ax2)

    #########################################################

    def save_log(self, sky_factor):

        objDict = {}

        objDict["index"] = "value"
        objDict["uuid"] = self.uuid
        objDict["User"] = os.getenv("HOST_USER").capitalize()
        objDict["Time"] = datetime.now()
        objDict["Name"] = self.name
        objDict["X_pixels"] = self.x_max
        objDict["Y_pixels"] = self.y_max
        objDict["R_max"] = self.r_max
        objDict["X0"] = self.x0
        objDict["Y0"] = self.y0
        objDict["a"] = "%.3f" % self.a
        objDict["b"] = "%.3f" % self.b
        objDict["sky_med"] = "%.3f" % self.params["background"]["median"]
        objDict["sky_avg"] = "%.3f" % self.params["background"]["mean"]
        objDict["sky_std"] = "%.3f" % self.params["background"]["std"]
        objDict["r0"] = r0 = self.params["second_elliprof"]["r0"]
        objDict["c_kron"] = c_kron = self.params["second_elliprof"]["c_kron"]
        objDict["r1"] = r1 = self.outerR(c_kron)
        objDict["k"] = k = self.params["second_elliprof"]["k_ellipse"]
        objDict["nr"] = int(np.round((r1 - r0) / k))
        objDict["options"] = self.params["second_elliprof"]["option"]
        objDict["sky_factor"] = "%.3f" % sky_factor
        objDict["sky"] = int(sky_factor * self.sky_med)
        objDict["initial_sky_med"] = "%.3f" % self.sky_med
        objDict["initial_sky_avg"] = "%.3f" % self.sky_ave
        objDict["initial_sky_std"] = "%.3f" % self.sky_std

        objDict["obj_root"] = self.objRoot

        objDict["resid_name"] = self.objRoot + "resid.000"
        objDict["model_name"] = self.objRoot + "model.000"
        objDict["back_mask"] = self.objRoot + "back_mask.fits"
        objDict["ellipseFile"] = self.objRoot + "elliprof.000"

        main_key = "backSextract"
        objDict["BXT"] = self.params[main_key]["threshold"]

        main_key = "naiveSextract"
        objDict["NXM"] = self.params[main_key]["minarea"]
        objDict["NXT"] = self.params[main_key]["threshold"]
        objDict["NXS"] = self.params[main_key]["smooth"]

        main_key = "basic_elliprof"
        objDict["BER"] = self.params[main_key]["r0"]
        objDict["BEC"] = self.params[main_key]["c_kron"]
        objDict["BES"] = self.params[main_key]["sky_factor"]
        objDict["BEK"] = self.params[main_key]["k_ellipse"]
        objDict["BEO"] = self.params[main_key]["option"]

        main_key = "second_elliprof"
        objDict["SER"] = self.params[main_key]["r0"]
        objDict["SEC"] = self.params[main_key]["c_kron"]
        objDict["SEF"] = self.params[main_key]["sky_factor"]
        objDict["SEK"] = self.params[main_key]["k_ellipse"]
        objDict["SEO"] = self.params[main_key]["option"]
        objDict["SEM"] = self.params[main_key]["minarea"]
        objDict["SET"] = self.params[main_key]["threshold"]
        objDict["SES"] = self.params[main_key]["smooth"]
        objDict["SEN"] = self.params[main_key]["renuc"]

        ########

        df = pd.DataFrame.from_dict(objDict, orient="index", columns=["value"])

        key = "description"
        df[key] = ""

        ########
        df.at["index", key] = "description"
        df.at["uuid", key] = "Unique Identifier Code"
        df.at["Name", key] = "Object Name"
        df.at["User", key] = "User Name"
        df.at["Time", key] = "Modification Time"
        df.at["X_pixels", key] = "X-dimension of image [pixel]"
        df.at["Y_pixels", key] = "Y-dimension of image [pixel]"
        df.at[
            "R_max", key
        ] = "maximum horizontal/vertical distance from center to the image border [pixel]"
        df.at["X0", key] = "Object Center X0 [pixel]"
        df.at["Y0", key] = "Object Center Y0 [pixel]"
        df.at["a", key] = "semi-major axis [pixel]"
        df.at["b", key] = "semi-minor axis [pixel]"
        df.at["sky_med", key] = "median sky background after model subtraction"
        df.at["sky_avg", key] = "mean sky background after model subtraction"
        df.at[
            "sky_std", key
        ] = "1-sigma standard deviation of the sky background after model subtraction"
        df.at["r0", key] = "elliprof: inner fit radius"
        df.at["r1", key] = "elliprof: outer fit radius"
        df.at["nr", key] = "elliprof: number of fitted radii "
        df.at["k", key] = "nr=[r1/k]"
        df.at["c_kron", key] = "Kron radius factor"
        df.at["options", key] = "elliprof: options"
        df.at["sky_factor", key] = "sky factor"
        df.at["sky", key] = "sky level = sky_factor*initial_sky_median"
        df.at["initial_sky_med", key] = "initial sky median"
        df.at["initial_sky_avg", key] = "initial sky mean"
        df.at["initial_sky_std", key] = "initial sky standard deviation"

        df.at["obj_root", key] = "name of the outputs folder"

        df.at["resid_name", key] = "residual image [fits]"
        df.at["model_name", key] = "model image [fits]"
        df.at["back_mask", key] = "background mask [fits]"
        df.at["ellipseFile", key] = "ellipse file [text]"

        df.at["BXT", key] = "backSourceExtract::threshold"

        df.at["NXM", key] = "naiveSourceExtract::minarea"
        df.at["NXT", key] = "naiveSourceExtract::threshold"
        df.at["NXS", key] = "naiveSourceExtract::smooth"

        df.at["BER", key] = "basic_elliprof::r0"
        df.at["BEC", key] = "basic_elliprof::c_kron"
        df.at["BES", key] = "basic_elliprof::sky_factor"
        df.at["BEK", key] = "basic_elliprof::k_ellipse"
        df.at["BEO", key] = "basic_elliprof::option"

        df.at["SER", key] = "second_elliprof::r0"
        df.at["SEC", key] = "second_elliprof::c_kron"
        df.at["SEF", key] = "second_elliprof::sky_factor"
        df.at["SEK", key] = "second_elliprof::k_ellipse"
        df.at["SEO", key] = "second_elliprof::option"
        df.at["SEM", key] = "second_elliprof::minarea"
        df.at["SET", key] = "second_elliprof::threshold"
        df.at["SES", key] = "second_elliprof::smooth"
        df.at["SEN", key] = "second_elliprof::renuc"

        ########

        df = df.reset_index()
        logFile = self.objRoot + "../" + self.name + "_model_log.csv"

        if not exists(logFile):
            xcmd(
                "echo '###### uuid:'" + self.uuid + "  > " + logFile + ".temp",
                verbose=False,
            )  # header
            np.savetxt(logFile, df.values, fmt="%20s , %60s , %80s")

            xcmd("cat " + logFile + " >> " + logFile + ".temp", verbose=False)
            xcmd("mv " + logFile + ".temp " + logFile, verbose=False)
        else:
            xcmd(
                "echo '###### uuid: '" + self.uuid + "  > " + logFile + ".temp~",
                verbose=False,
            )  # header

            np.savetxt(logFile + ".temp", df.values, fmt="%20s , %60s , %80s")

            xcmd("echo   >> " + logFile + ".temp", verbose=False)

            xcmd(
                "cat " + logFile + ".temp" + " >> " + logFile + ".temp~", verbose=False
            )
            xcmd("cat " + logFile + " >> " + logFile + ".temp~", verbose=False)

            xcmd("mv " + logFile + ".temp~ " + logFile, verbose=False)
            xcmd("rm " + logFile + ".temp", verbose=False)

        print("Log File: ", logFile)

        return df

    def insert_existing_profile(self, profile=None, sky=None):

        model = 0

        root = self.objRoot
        suffix = ".%03d" % model
        name = self.name

        if sky is None:
            sky = self.sky_med

        cwd = os.getcwd()
        os.chdir(root)

        # imorting common.mask
        xcmd(
            "cp {} ./common.mask".format(self.config + "/common.mask"),
            verbose=False,
        )
        Cmask = "common.mask"

        Dmask = self.inFolder + "{}/{}j.dmask".format(self.name, self.name)

        # buidling mask1
        self.inputMaks(Cmask, mask=1)
        if os.path.exists(Dmask):
            self.inputMaks(Dmask, mask=0)
            self.addMasks(maskList=[0, 1], mask=1)

        mask = 1
        maskName = "mask" + ".%03d" % mask

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16, 5))

        ## Calculating the number of crossing ellipses, the generated model = 0, from previous linen_cross = Xellipses(obj.list_ellipses(model=0))
        self.tv(options="log", ax=ax1)
        ax1.set_title(self.name, fontsize=14)

        im, h = self.maskOpen(mask=1)
        ax2.imshow(np.flipud(im))
        ax2.set_title("Mask 1", fontsize=14)

        # build model 0
        if profile is None:
            PRF = self.inFolder + "{}/{}j.prf".format(self.name, self.name)
        else:
            PRF = profile
        model = 0
        modelName = "model" + ".%03d" % model
        residName = "resid" + ".%03d" % model
        if os.path.exists(PRF):
            xcmd(
                "cp {} {}".format(PRF, modelName),
                verbose=False,
            )
        else:
            raise Exception("Profile ({}) does not exist !".format(PRF))

        self.tv_model(model=0, ax=ax3, options="sqrt")
        ax3.set_title("Profile", fontsize=14)

        objFits = self.inFolder + "{}/{}j.fits".format(name, name)
        xcmd("cp {} ./{}j.fits".format(objFits, name), verbose=False)
        objFits = "{}j.fits".format(name)

        ## Monsta script
        script = (
            """
        string name '"""
            + self.name
            + """'
        rd 1 '"""
            + objFits
            + """'
        sc 1 """
            + str(sky)
            + """                            ! sky subtraction
        rd 3 """
            + modelName
            + """
        si 1 3                               ! object - model
        rd 2 """
            + maskName
            + """
        mi 1 2                                ! multiply by mask
        wd 1 """
            + residName
            + """
        tv 1 JPEG="""
            + residName
            + """.jpg
        q
        
        """
        )

        self.run_monsta(script, root + "monsta.pro", root + "monsta.log")

        self.tv_resid(model=0, ax=ax4, options="sqrt")
        ax4.set_title("Residual", fontsize=14)

        # self.tv_resid(model=0, ax=ax3, options="sqrt")
        # ax3.set_title("Residual", fontsize=14)

        # if pngName is None:
        #     pngName = self.objRoot + "/" + self.name + "_basic_model.png"
        # else:
        #     pngName = self.objRoot + "/" + pngName

        # plt.savefig(pngName)
        # print("fig. name: ", pngName)

        os.chdir(cwd)

        return (ax1, ax2, ax3, ax4)


#########################################################
