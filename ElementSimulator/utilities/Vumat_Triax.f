program Triaxial_test
   implicit none

   ! IMPORTANT: VUMAT allows single AND double precision
   integer, parameter :: dp = selected_real_kind(15)
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
   real(dp), dimension(nstatev) :: statevariables, inpstate, outstate
   real(dp), dimension(ndir + nshr) :: stress, strain
   real(dp), dimension(1, ndir + nshr) :: inpstress, outstress1, outstress2
   real(dp), dimension(1, ndir + nshr) :: inpstrain1, inpstrain2, refstrain
   real(dp) :: dt, initial_voidratio, triax_pressure, modstrain
   real(dp) :: diff1, diff2
   real(dp) :: contraction, fak2, pressure_deviation, compared_strain
   real(dp), parameter :: tolerable_pressure_deviation = 0.000001_dp
   integer, parameter :: maxiter = --maxiter--
   real(dp), dimension(6, maxiter) :: sim_strains
   integer :: idx, innercounter, strainidx, filenr, stat
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
   initial_voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Time increment to be used
   dt = --timeincrement--

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! After which height fraction shall the triaxial simulation end
   contraction = --triax_maxcontraction--

   ! Give initial stress and strain matrices (in vector form)
   triax_pressure = --triax_pressure--
   stress = [triax_pressure, triax_pressure, triax_pressure, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [-1.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt

   pressure_deviation = abs(tolerable_pressure_deviation*triax_pressure)
   fak2 = 0.0001_dp
   compared_strain = 0.0_dp
   inpstress(1, :) = stress
   inpstate = statevariables


   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f12.5, a, f12.5, a, f12.5)') 0.0, '   ', 0.0, '   ', 0.0

   idx = 1
   strainidx = 0
   sim_strains = 0.0_dp
   breakall = .False.

   call cpu_time(starttime)
   triax_compression : &
   do
      if (compared_strain > contraction) then
         exit triax_compression
      end if
      refstrain(1, :) = strain
      inpstrain1(1, :) = [refstrain(1, 1), 0.0_dp, 0.0_dp, refstrain(1, 4), refstrain(1, 5), refstrain(1, 6)]
      call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                  materialname, coordMp, charLength, materialparameters, density, inpstrain1, &
                  relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                  enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                  outstress1, outstate, enerInternNew, enerInelasNew)

      diff1 = outstress1(1, 2) - inpstress(1, 2)

      inpstrain2(1, :) = [refstrain(1, 1), fak2*refstrain(1, 1), fak2*refstrain(1, 1), &
                           refstrain(1, 4), refstrain(1, 5), refstrain(1, 6)]
      call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                 materialname, coordMp, charLength, materialparameters, density, inpstrain2, &
                 relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                 enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                 outstress2, outstate, enerInternNew, enerInelasNew)
      diff2 = outstress2(1, 2) - inpstress(1, 2)

      innercounter = 0
      minimize_difference : &
      do
         if (abs(diff2) < pressure_deviation) then
            exit minimize_difference
         end if

         if (innercounter > 10) then
            write(*, *) 'Strain increment halved'
            refstrain = refstrain/2.0_dp

            inpstrain1(1, :) = [refstrain(1, 1), 0.0_dp, 0.0_dp, &
                                 refstrain(1, 4), refstrain(1, 5), refstrain(1, 6)]
            call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                        materialname, coordMp, charLength, materialparameters, density, inpstrain1, &
                        relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                        enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                        outstress1, outstate, enerInternNew, enerInelasNew)
            diff1 = outstress1(1, 2) - inpstress(1, 2)

            inpstrain2(1, :) = [refstrain(1, 1), fak2*refstrain(1, 1), fak2*refstrain(1, 1), &
                                 refstrain(1, 4), refstrain(1, 5), refstrain(1, 6)]
            call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                       materialname, coordMp, charLength, materialparameters, density, inpstrain2, &
                       relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                       enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                       outstress2, outstate, enerInternNew, enerInelasNew)
            diff2 = outstress2(1, 2) - inpstress(1, 2)
            innercounter = 0
         end if

         modstrain = (diff2*inpstrain1(1, 2) - diff1*inpstrain2(1, 2))/(diff2 - diff1)
         inpstrain1 = inpstrain2
         diff1 = diff2
         inpstrain2(1, 2:3) = modstrain

         call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                    materialname, coordMp, charLength, materialparameters, density, inpstrain2, &
                    relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                    enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                    outstress1, outstate, enerInternNew, enerInelasNew)
         diff2 = outstress1(1, 2) - inpstress(1, 2)

         refstrain = inpstrain2
         innercounter = innercounter + 1
         strainidx = strainidx + 1

         ! Check for NaN entries
         if (diff2 /= diff2) then
            write(*, *) 'Error: NaN entries found'
            breakall = .True.
            exit minimize_difference
         end if
         if (strainidx > maxiter) then
            write(*, *) 'Error: Problem in triax loop'
            breakall = .True.
            exit minimize_difference
         end if
      end do minimize_difference
      if (breakall) then
         exit triax_compression
      end if

      strainidx = 0

      inpstress = outstress1
      inpstate = outstate

      sim_strains(:, idx + 1) = sim_strains(:, idx) + refstrain(1, :)
      compared_strain = abs(sim_strains(1, idx))

      ! Writing: eps1 in %, eps_v in %, q in kPa
      write(filenr, '(f12.5, a, f12.5, a, f12.5)') 100.0_dp*sim_strains(1, idx), '   ', &
            100.0_dp*sum(sim_strains(1:3, idx)), '   ', -(outstress1(1, 1) - outstress1(1, 2))

      idx = idx + 1
      if (idx > maxiter) then
         write(*, *) 'Error: Maximum number of specified iterations reached'
         exit triax_compression
      end if
   end do triax_compression
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Triaxial_test
