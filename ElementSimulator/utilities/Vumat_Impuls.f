program Singleresponse_test
   implicit none

   ! IMPORTANT: VUMAT allows single AND double precision
   integer, parameter :: dp = selected_real_kind(15)
   !
   integer, parameter :: nblock = 1
   integer, parameter :: ndir = 3
   integer, parameter :: nshr = 3
   integer, parameter :: nstatev = 20
   integer, parameter :: nfieldv = 1
   integer, parameter :: nprops = --numparameter--
   integer :: lanneal
   real(dp) :: stepTime, totalTime
   real(dp), dimension(1) :: charLength, density, tempOld, enerInternOld, enerInelasOld, tempNew, &
                             enerInternNew, enerInelasNew
   real(dp), dimension(1, 6) :: stretchOld, stretchNew
   real(dp), dimension(1, 3) :: relSpinInc
   real(dp), dimension(1, 9) :: defgradOld, defgradNew
   real(dp), dimension(1, 1) :: fieldOld, fieldNew
   real(dp), dimension(1, 1) :: coordMp
   !
   character(len=80) :: materialname
   real(dp), dimension(nprops) :: materialparameters
   real(dp), dimension(nstatev) :: statevariables
   real(dp), dimension(ndir + nshr) :: stress, strain
   real(dp), dimension(1, nstatev) :: inpstate, outstate
   real(dp), dimension(1, ndir + nshr) :: inpstress, outstress
   real(dp), dimension(1, ndir + nshr) :: inpstrain
   real(dp) :: dt, initial_voidratio
   integer :: filenr, stat
   real(dp) :: starttime, endtime

   lanneal = 0
   stepTime = --starttime--
   totalTime = --starttime--

   coordMp = 0.0_dp
   charLength = 0.0_dp
   density = 0.0_dp
   relSpinInc = 0.0_dp
   tempOld = 0.0_dp
   stretchOld = 0.0_dp
   defgradOld = 0.0_dp
   fieldOld = 0.0_dp
   enerInternOld = 0.0_dp
   enerInelasOld = 0.0_dp
   tempNew = 0.0_dp
   stretchNew = 0.0_dp
   defgradNew = 0.0_dp
   fieldNew = 0.0_dp
   enerInternNew = 0.0_dp
   enerInelasNew = 0.0_dp

   ! Decide which constitutive model to use by materialname
   materialname = '--materialname--'

   ! List material parameters to be used
   initial_voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Time increment to be used
   dt = --timeincrement--

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! Give initial stress and strain matrices (in vector form)
   stress = [--impuls_stress--]
   strain = [--impuls_strain--]*dt


   inpstress(1, :) = stress
   outstress(1, :) = stress
   inpstate(1, :) = statevariables
   inpstrain(1, :) = strain

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   call cpu_time(starttime)
   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -inpstress(1, 1), '   ', -inpstress(1, 2), '   ', -inpstress(1, 3), '   ', &
      -inpstress(1, 4), '   ', -inpstress(1, 5), '   ', -inpstress(1, 6), '   ', inpstate(1, 1)

   call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
               materialname, coordMp, charLength, materialparameters, density, inpstrain, &
               relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
               enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
               outstress, outstate, enerInternNew, enerInelasNew)
   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -outstress(1, 1), '   ', -outstress(1, 2), '   ', -outstress(1, 3), '   ', &
      -outstress(1, 4), '   ', -outstress(1, 5), '   ', -outstress(1, 6), '   ', outstate(1, 1)
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Singleresponse_test
