program Triaxial_test
   use Preparation, only: Get_Material, Prepare_State
   implicit none

   ! IMPORTANT: UMAT allows single AND double precision, but some implementations require double precision
   integer, parameter :: dp = selected_real_kind(15)
   !
   integer, parameter :: ndi = 3
   integer, parameter :: nshr = 3
   integer, parameter :: ntens = 6
   integer, parameter :: nstatv = 20
   integer, parameter :: nprops = --numparameter--
   real(dp), dimension(ntens) :: ddsddt, drplde, stran
   real(dp), dimension(ntens, ntens) :: ddsdde
   real(dp), dimension(3, 3) :: drot, dfgrd0, dfgrd1
   real(dp), dimension(3) :: coords
   real(dp), dimension(2) :: time
   real(dp), dimension(1) :: predef, dpred
   real(dp) :: sse, spd, scd, rpl, drpldt, temp, dtemp, celent, pnewdt
   integer, dimension(4) :: jstep
   integer :: noel, npt, layer, kspt, kinc
   !
   character(len=80) :: materialname, check_materialname
   character(len=40) :: material_description
   real(dp), dimension(16) :: materialparam_vec
   real(dp), dimension(nprops) :: materialparameters
   real(dp), dimension(nstatv) :: statevariables, inpstate, inoutstate
   real(dp), dimension(ntens) :: stress, inpstress, inoutstress1, inoutstress2
   real(dp), dimension(ntens) :: strain, inpstrain1, inpstrain2, refstrain
   real(dp), dimension(6) :: intergranular_strain
   real(dp) :: dt, voidratio, triax_pressure, modstrain
   real(dp) :: diff1, diff2
   real(dp) :: contraction, fak2, pressure_deviation, compared_strain
   real(dp), parameter :: tolerable_pressure_deviation = 0.000001_dp
   integer, parameter :: maxiter = --maxiter--
   real(dp), dimension(6, maxiter) :: sim_strains
   integer :: ixx, jxx
   integer :: idx, innercounter, strainidx, filenr, stat
   logical :: breakall
   real(dp) :: starttime, endtime
   logical :: is_success, igran_active

   ddsddt = 0.0_dp
   drplde = 0.0_dp
   stran = 0.0_dp
   ddsdde = 0.0_dp
   drot = reshape([(1.0_dp, (0.0_dp, ixx = 1, 3), jxx = 1, 2), 1.0_dp], [3, 3])
   dfgrd0 = drot
   dfgrd1 = drot
   coords = 0.0_dp
   !
   predef = 0.0_dp
   dpred = 0.0_dp
   celent = 0.0_dp
   pnewdt = 0.0_dp
   sse = 0.0_dp
   spd = 0.0_dp
   scd = 0.0_dp
   rpl = 0.0_dp
   drpldt = 0.0_dp
   temp = 0.0_dp
   dtemp = 0.0_dp
   !
   jstep = 0
   noel = 0
   npt = 0
   layer = 0
   kspt = 0
   kinc = 0

   ! Decide which constitutive model to use by materialname
   check_materialname = '--materialname--'
   material_description = '--materialdescription--'
   igran_active = --igranactive--

   ! Time increment to be used
   time = [--starttime--, --starttime--]
   dt = --timeincrement--

   ! List material parameters to be used
   voidratio = --initialvoidratio--
   intergranular_strain = [--intergranularstrain--]
   ! FIXME: Temporary switch
   intergranular_strain(1:2) = [intergranular_strain(2), intergranular_strain(1)]

   ! After which height fraction shall the triaxial simulation end
   contraction = --triax_maxcontraction--

   ! Give initial stress and strain matrices (in vector form)
   triax_pressure = --triax_pressure--
   stress = [triax_pressure, triax_pressure, triax_pressure, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [-1.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt

   pressure_deviation = abs(tolerable_pressure_deviation*triax_pressure)
   fak2 = 0.0001_dp
   compared_strain = 0.0_dp


   call Get_Material(material_description=material_description, igran_active=igran_active, &
      constitutive_model_name=check_materialname(1:9), adj_name=materialname, nu=0.25_dp, &
      materialparameters=materialparam_vec, success=is_success)
   if (.not. is_success) then
      stop 'Failed'
   end if
   materialparameters = materialparam_vec(1:nprops)

   call Prepare_State(constitutive_model_name=check_materialname(1:9), voidratio=voidratio, &
      intergranular_strain=intergranular_strain, igran_active=igran_active, integration_method=1, &
      first_dt=dt, integration_tolerance=0.0001_dp, statevariables=statevariables, success=is_success)
   if (.not. is_success) then
      stop 'Failed'
   end if


   ! Adjust input stress and input strain to UMAT defaults
   stress = [stress(1:4), stress(6), stress(5)]
   strain = [strain(1:3), 2.0_dp*strain(4), 2.0_dp*strain(6), 2.0_dp*strain(5)]

   inpstress = stress
   inpstate = statevariables
   inoutstate = statevariables


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

      inoutstress1 = inpstress
      inoutstress2 = inpstress
      refstrain = strain
      inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, refstrain(4), refstrain(5), refstrain(6)]
      inoutstate = inpstate                                         ! Reset state before call
      call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                stran, inpstrain1, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                dfgrd1, noel, npt, layer, kspt, jstep, kinc)

      diff1 = inoutstress1(2) - inpstress(2)

      inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                     refstrain(4), refstrain(5), refstrain(6)]
      inoutstate = inpstate                                          ! Reset state before call
      call UMAT(inoutstress2, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                dfgrd1, noel, npt, layer, kspt, jstep, kinc)
      inoutstate = inpstate                                          ! Reset state
      diff2 = inoutstress2(2) - inpstress(2)

      innercounter = 0
      minimize_difference : &
      do
         if (abs(diff2) < pressure_deviation) then
            exit minimize_difference
         end if

         if (innercounter > 10) then
            write(*, *) 'Strain increment halved'
            refstrain = refstrain/2.0_dp

            inoutstress1 = inpstress
            inoutstress2 = inpstress

            inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, refstrain(4), refstrain(5), refstrain(6)]
            inoutstate = inpstate                                    ! Reset state before call
            call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                      stran, inpstrain1, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                      ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                      dfgrd1, noel, npt, layer, kspt, jstep, kinc)
            diff1 = inoutstress1(2) - inpstress(2)

            inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                           refstrain(4), refstrain(5), refstrain(6)]
            inoutstate = inpstate                                    ! Reset state before call
            call UMAT(inoutstress2, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                      stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                      ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                      dfgrd1, noel, npt, layer, kspt, jstep, kinc)
            diff2 = inoutstress2(2) - inpstress(2)
            innercounter = 0
         end if

         modstrain = (diff2*inpstrain1(2) - diff1*inpstrain2(2))/(diff2 - diff1)
         inpstrain1 = inpstrain2
         diff1 = diff2
         inpstrain2(2:3) = modstrain

         inoutstress1 = inpstress
         inoutstate = inpstate                                       ! Reset state before call
         call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                   stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                   ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                   dfgrd1, noel, npt, layer, kspt, jstep, kinc)
         diff2 = inoutstress1(2) - inpstress(2)

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

      inpstress = inoutstress1
      inpstate = inoutstate

      sim_strains(:, idx + 1) = sim_strains(:, idx) + refstrain
      compared_strain = abs(sim_strains(1, idx))

      ! Writing: eps1 in %, eps_v in %, q in kPa
      write(filenr, '(f12.5, a, f12.5, a, f12.5)') 100.0_dp*sim_strains(1, idx), '   ', &
            100.0_dp*sum(sim_strains(1:3, idx)), '   ', -(inoutstress1(1) - inoutstress1(2))

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
