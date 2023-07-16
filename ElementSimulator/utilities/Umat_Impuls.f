program Singleresponse_test
   use Preparation, only: Get_Material, Prepare_State, Postprocess_State
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
   real(dp), dimension(nstatv) :: statevariables, inoutstate
   real(dp), dimension(ntens) :: stress, inoutstress
   real(dp), dimension(ntens) :: strain, inpstrain
   real(dp), dimension(6) :: intergranular_strain
   real(dp) :: dt, voidratio
   integer :: filenr, stat, ixx, jxx
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

   ! Give initial stress and strain matrices (in vector form)
   stress = [--impuls_stress--]
   strain = [--impuls_strain--]*dt


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

   inoutstress = stress
   inoutstate = statevariables
   inpstrain = strain

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   call cpu_time(starttime)
   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -inoutstress(1), '   ', -inoutstress(2), '   ', -inoutstress(3), '   ', &
      -inoutstress(4), '   ', -inoutstress(6), '   ', -inoutstress(5), '   ', voidratio

   call UMAT(inoutstress, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
               stran, inpstrain, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
               ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
               dfgrd1, noel, npt, layer, kspt, jstep, kinc)

   call Postprocess_State(constitutive_model_name=check_materialname(1:9), inoutstate=inoutstate, &
      nstates=nstatv, voidratio=voidratio, intergranular_strain=intergranular_strain, jacobian=ddsdde)

   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -inoutstress(1), '   ', -inoutstress(2), '   ', -inoutstress(3), '   ', &
      -inoutstress(4), '   ', -inoutstress(6), '   ', -inoutstress(5), '   ', voidratio
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Singleresponse_test
