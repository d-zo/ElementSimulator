program Oedometric_test
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
   real(dp), dimension(--pressure_entries--) :: oedo_pressure
   real(dp) :: dt, sigma1, voidratio, numbersign
   integer :: istep, idx, filenr, stat
   integer, parameter :: maxiter = --maxiter--
   logical :: breakall
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
   voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Time increment to be used
   dt = --timeincrement--

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = voidratio

   ! State loads
   oedo_pressure = [ &
   --oedo_pressure--]

   ! Give initial stress and strain matrices (in vector form)
   sigma1 = oedo_pressure(1)
   stress = [sigma1/2.0_dp, sigma1, sigma1/2.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [0.0_dp, -0.05_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt


   inpstress(1, :) = stress
   outstress(1, :) = stress
   inpstate(1, :) = statevariables

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f13.6, a, f13.6)') -stress(2), '   ', voidratio

   idx = 1
   breakall = .False.

   call cpu_time(starttime)
   loading_cycle: &
   do istep = 2, size(oedo_pressure)
      numbersign = (-1.0_dp)**istep
      inpstrain(1, :) = numbersign*strain
      loading_loop: &
      do
         if (numbersign*outstress(1, 2) < numbersign*oedo_pressure(istep)) then
            exit loading_loop
         end if
         call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                    materialname, coordMp, charLength, materialparameters, density, inpstrain, &
                    relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                    enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                    outstress, outstate, enerInternNew, enerInelasNew)
         ! FIXME: Check if any stress is complex or nan

         write(filenr, '(f13.6, a, f13.6)') -outstress(1, 2), '   ', outstate(1, 1)

         inpstress = outstress
         inpstate = outstate
         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Maximum number of specified iterations reached'
            breakall = .True.
            exit loading_loop
         end if
      end do loading_loop
      if (breakall) then
         exit loading_cycle
      end if
   end do loading_cycle
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Oedometric_test
